class GameState:
    def __init__(self, x, y, map_id, badges, party_size=0, first_species=0):
        self.x = x
        self.y = y
        self.map_id = map_id
        self.badges = badges
        self.party_size = party_size
        self.first_species = first_species

    def position(self):
        return (self.map_id, self.x, self.y)
