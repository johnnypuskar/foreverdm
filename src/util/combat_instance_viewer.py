import vpython as vp
import asyncio

class CombatInstanceViewer:

    class TokenRender:
        def __init__(self, token, sphere, box):
            self.token = token
            self.sphere = sphere
            self.box = box
        
        def update(self, color = vp.color.red):
            token_center_x = self.token.get_position()[0] + (self.token.get_size().radius / 2.0 - 2.5)
            token_y = self.token.get_position()[2]
            token_center_z = self.token.get_position()[1] + (self.token.get_size().radius / 2.0 - 2.5)

            self.sphere.pos = vp.vector(token_center_x, token_y, token_center_z)
            self.box.pos = vp.vector(token_center_x, token_y - 0.4, token_center_z)
            self.box.size = vp.vector(self.token.get_size().radius / 5 - 0.05, 0.2, self.token.get_size().radius / 5 - 0.05)

            self.sphere.color = color
            self.box.color = color

    def __init__(self):
        self.running = False
        self.instance = None
        self.tokens = []

    async def await_next(self):
        self.running = True
        try:
            while self.running:
                for token in self.tokens:
                    color = vp.color.red
                    current_name = self.instance.get_statblock(self.instance._turn_order[self.instance._current]).get_name()
                    if token.token.get_name() == current_name:
                        color = vp.color.blue
                    token.update(color)
                await asyncio.sleep(1/60)
        except Exception as e:
            print(f"Viewer error: {e}")
    
    def start_background_updates(self):
        loop = asyncio.get_event_loop()
        self.update_task = loop.create_task(self.await_next())

    def stop_background_updates(self):
        self.running = False
        if hasattr(self, 'update_task'):
            self.update_task.cancel()

    def set_instance(self, instance):
        vcanvas = vp.canvas(width = 1000, height = 800, background = vp.color.white)
        vcanvas.select()

        self.instance = instance
        map = instance._map

        for tile in map.get_all_tiles():
            if tile.x == 0 or tile.y == 0:
                if tile.x != tile.y:
                    nonzero = tile.x if tile.x != 0 else tile.y
                    vp.label(pos=vp.vector(tile.x - (1 if tile.x == 0 else 0), tile.height, tile.y - (1 if tile.y == 0 else 0)), text=f"{nonzero}", color=vp.color.black)
                else:
                    vp.label(pos=vp.vector(-1, tile.height, 0), text="0", color=vp.color.black)
                    vp.label(pos=vp.vector(0, tile.height, -1), text="0", color=vp.color.black)
            vp.box(pos=vp.vector(tile.x, tile.height, tile.y), size=vp.vector(0.95, 0.95, 0.95), color=vp.color.white, opacity=0.1)
            if tile.height > 0:
                vp.box(pos=vp.vector(tile.x, (tile.height - 1) / 2.0, tile.y), size=vp.vector(1, tile.height, 1), color=vp.color.gray(0.4))
            for wall_height in range(tile.height, map._max_height):
                if not tile._wall_top.get_passable(wall_height):
                    vp.box(pos=vp.vector(tile.x, wall_height, tile.y - 0.45), size=vp.vector(1, 1, 0.1), color=vp.color.gray(0.5))
                if not tile._wall_left.get_passable(wall_height):
                    vp.box(pos=vp.vector(tile.x - 0.45, wall_height, tile.y), size=vp.vector(0.1, 1, 1), color=vp.color.gray(0.5))
                if not tile._wall_bottom.get_passable(wall_height):
                    vp.box(pos=vp.vector(tile.x, wall_height, tile.y + 0.45), size=vp.vector(1, 1, 0.1), color=vp.color.gray(0.5))
                if not tile._wall_right.get_passable(wall_height):
                    vp.box(pos=vp.vector(tile.x + 0.45, wall_height, tile.y), size=vp.vector(0.1, 1, 1), color=vp.color.gray(0.5))
        
        for token in map.get_tokens():
            sphere = vp.sphere(pos=vp.vector(token.get_position()[0], token.get_position()[2], token.get_position()[1]), radius=0.4, color=vp.color.red)
            box = vp.box(pos=vp.vector(token.get_position()[0], token.get_position()[2] - 0.45, token.get_position()[1]), size=vp.vector(0.95, 0.1, 0.95), color=vp.color.red)
            render = self.TokenRender(token, sphere, box)
            render.update()
            self.tokens.append(render)
        
        vp.button(text='Quit', bind=self.stop_background_updates)