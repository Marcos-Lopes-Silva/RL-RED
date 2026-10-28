class GameState:
    def __init__(self, x, y, map_id, badges, party_size=0, first_species=0, in_battle=0, enemy_hp=0, enemy_max_hp=0, enemy_debuff=0):
        self.x = x
        self.y = y
        self.map_id = map_id
        self.badges = badges
        self.party_size = party_size
        self.first_species = first_species
        self.in_battle = in_battle
        self.enemy_hp = enemy_hp
        self.enemy_max_hp = enemy_max_hp
        self.enemy_debuff = enemy_debuff

    def position(self):
        return (self.map_id, self.x, self.y)
