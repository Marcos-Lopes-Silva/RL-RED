from src.pokemon_ram import MemoryService, PokemonRAM

class StateBuilder:
    def __init__(self, memory_service: MemoryService):
        self.memory = memory_service

    def build(self):
        x, y = self.memory.get_player_pos()

        return [
            x,
            y,
            self.memory.get_value(PokemonRAM.MAP_ID),
            self.memory.get_value(PokemonRAM.BADGES),
            self.memory.get_value(PokemonRAM.PARTY_SIZE),
            self.memory.get_value(PokemonRAM.PARTY_SPECIES_ADDR),
            self.memory.in_battle(PokemonRAM.IN_BATTLE),
            self.memory.enemy_hp(PokemonRAM.ENEMY_HP),
            self.memory.enemy_max_hp(PokemonRAM.ENEMY_MAX_HP)
        ]

