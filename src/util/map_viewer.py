import vpython as vp

class MapViewer:
    running = False

    @staticmethod
    def refresh_loop():
        MapViewer.running = True
        vp.button(text='Quit', bind=lambda: setattr(MapViewer, 'running', False))
        while MapViewer.running:
            vp.rate(60)

    @staticmethod
    def view_map(map):
        if MapViewer.running:
            return
        
        vcanvas = vp.canvas(width = 1000, height = 800, background = vp.color.white)
        vcanvas.select()

        for tile in map.get_all_tiles():
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

        for token in map.get_token_spaces():
            vp.sphere(pos=vp.vector(token.get_position()[0], token.get_position()[2], token.get_position()[1]), radius=0.4, color=vp.color.red)
    
    @staticmethod
    def view_map_with_highlights(map, highlights):
        MapViewer.view_map(map)

        for pos in highlights:
            vp.box(pos=vp.vector(pos[0], pos[2], pos[1]), size=vp.vector(0.7, 0.7, 0.7), color=vp.color.purple, opacity=0.35)