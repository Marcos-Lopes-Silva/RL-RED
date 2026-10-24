from enum import IntEnum
from pyboy import PyBoy


class PokemonRAM(IntEnum):
    PLAYER_X = 0xD362
    PLAYER_Y = 0xD361
    MAP_ID = 0xD35E
    PARTY_SIZE = 0xD163
    BADGES = 0xD356
    OPPONENT_HP = 0xCFE7


class MemoryService:
    def __init__(self, pyboy: PyBoy):
        self.pyboy = pyboy

    def get_value(self, address: PokemonRAM) -> int:
        return self.pyboy.memory[address.value]

    def get_player_pos(self):
        return (
            self.get_value(PokemonRAM.PLAYER_X),
            self.get_value(PokemonRAM.PLAYER_Y),
        )

    def get_sprite_value(self, sprite_id: int, offset: int) -> int:
        base = 0xC100
        return self.pyboy.memory[base + sprite_id * 0x10 + offset]

    def get_sprite_y(self, sprite_id: int) -> int:
        return self.get_sprite_value(sprite_id, 0x4)

    def get_sprite_x(self, sprite_id: int) -> int:
        return self.get_sprite_value(sprite_id, 0x6)

    def get_sprite_direction(self, sprite_id: int) -> int:
        return self.get_sprite_value(sprite_id, 0x9)

    def get_sprite_movement(self, sprite_id: int) -> int:
        return self.get_sprite_value(sprite_id, 0x1)
