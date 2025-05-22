class Lobby:
    def __init__(self, id):
        self.id = id
        self.allowed_player_ids = set()
        self.players = set()
    
    def player_join(self, player_id):
        if self.player_allowed(player_id):
            self.players.add(player_id)
            return True
        return False
    
    def player_leave(self, player_id):
        if player_id in self.players:
            self.players.remove(player_id)
            return True
        return False

    def player_allowed(self, player_id):
        # return player_id in self.allowed_player_ids
        return True