class GameState:
    def __init__(self, x, y, map_id, badges):
        self.x = x
        self.y = y
        self.map_id = map_id
        self.badges = badges

    def position(self):
        return (self.x, self.y, self.map_id)
