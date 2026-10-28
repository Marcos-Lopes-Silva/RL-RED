from enum import IntEnum
from pyboy import PyBoy

class PokemonRAM(IntEnum):
    PLAYER_X = 0xD362
    PLAYER_Y = 0xD361
    MAP_ID = 0xD35E
    PARTY_SIZE = 0xD163
    PARTY_SPECIES_ADDR = 0xD164
    BADGES = 0xD356
    IN_BATTLE = 0xD057
    ENEMY_HP = 0xCFE5
    ENEMY_MAX_HP = 0xCFF3


class MemoryService:
    def __init__(self, pyboy: PyBoy):
        self.pyboy = pyboy

    def get_value(self, address: PokemonRAM) -> int:
        return self.pyboy.memory[address.value]

    def get_word(self, address: PokemonRAM) -> int:
        return (self.pyboy.memory[address.value] << 8) | self.pyboy.memory[address.value + 1]

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

    def in_battle(self, in_battle) -> int:
        v = self.get_value(in_battle)
        return v if v in (1, 2) else 0

    def enemy_hp(self, enemy_hp) -> int:
        return self.get_word(enemy_hp)

    def enemy_max_hp(self, enemy_max_hp) -> int:
        return self.get_word(enemy_max_hp)