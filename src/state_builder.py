from src.pokemon_ram import MemoryService, PokemonRAM

class StateBuilder:
    def __init__(self, memory_service):
        self.memory = memory_service

    def build(self):
        x, y = self.memory.get_player_pos()

        return [
            x,
            y,
            self.memory.get_value(PokemonRAM.MAP_ID),
            self.memory.get_value(PokemonRAM.BADGES),
        ]

