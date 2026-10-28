from abc import ABC, abstractmethod
import math
from collections import defaultdict
from src.game_state import GameState

GRASS_TRIGGER_Y = 1
GRASS_TRIGGER_X = 10

BATTLE_TRIGGER_Y = 4
BATTLE_TRIGGER_X = 6

class RewardSystem:
    def __init__(self, strategies):
        self.strategies = strategies

    def compute(self, prev_state, current_state):
        return sum(s.compute(prev_state, current_state) for s in self.strategies)

    def reset(self, initial_state=None):
        for s in self.strategies:
            s.reset(initial_state)


class RewardStrategy(ABC):
    @abstractmethod
    def compute(self, prev_state, current_state) -> float:
        pass

    def reset(self, initial_state=None):
        pass


class ProgressReward(RewardStrategy):
    def __init__(self):
        self.visited_maps = set()

    def reset(self, initial_state: GameState=None):
        self.visited_maps.clear()
        if initial_state is not None:
            self.visited_maps.add(initial_state.map_id)

    def compute(self, prev_state: GameState, current_state: GameState):
        reward = 0.0
        if current_state.badges > prev_state.badges:
            reward += 100.0
        if current_state.map_id not in self.visited_maps:
            self.visited_maps.add(current_state.map_id)
            reward += 5.0
        return reward


class NoveltyReward(RewardStrategy):
    def __init__(self):
        self.visited = set()

    def reset(self, initial_state: GameState=None):
        self.visited.clear()
        if initial_state is not None:
            self.visited.add((initial_state.map_id, initial_state.x, initial_state.y))


    def compute(self, prev_state: GameState, current_state: GameState):
        key = (current_state.map_id, current_state.x, current_state.y)
        if key in self.visited:
            return -0.02
        self.visited.add(key)
        return 0.35


class StagnationPenalty(RewardStrategy):
    def __init__(self, grace=15, penalty=-0.02):
        self.grace = grace
        self.penalty = penalty
        self.still = 0

    def reset(self, initial_state: GameState=None):
        self.still = 0

    def compute(self, prev_state: GameState, current_state: GameState):
        if prev_state.position() == current_state.position():
            self.still += 1
            return self.penalty if self.still > self.grace else 0.0
        self.still = 0
        return 0.0


class PotentialFunction:
    def __init__(self):
        self.max_distance = 0

    def compute(self, state: GameState):
        return state.x + state.y + (state.map_id * 1000)


class PotentialReward(RewardStrategy):
    def __init__(self, potential_fn, gamma=0.99):
        self.potential_fn = potential_fn
        self.gamma = gamma

    def compute(self, prev_state, current_state):
        phi_s = self.potential_fn.compute(prev_state)
        phi_s_next = self.potential_fn.compute(current_state)

        return (phi_s_next - phi_s) * 0.001


class MovementReward(RewardStrategy):
    def compute(self, prev_state, current_state):
        if prev_state.position() != current_state.position():
            return 0.01
        return 0.0

class BacktrackPenalty(RewardStrategy):
    def __init__(self, window=50, penalty=-.5):
        self.window = window
        self.penalty = penalty
        self.previous_map = None
        self.steps_since_change = 0

    def reset(self, initial_state: GameState=None):
        self.previous_map = None
        self.steps_since_change = 0

    def compute(self, prev_state: GameState, current_state: GameState):
        self.steps_since_change += 1

        if current_state.map_id == prev_state.map_id:
            return 0.0

        reward = 0.0
        if (current_state.map_id == self.previous_map
                and self.steps_since_change <= self.window):
            reward = self.penalty

        self.previous_map = prev_state.map_id
        self.steps_since_change = 0
        return reward

class StarterReward(RewardStrategy):
    def __init__(self, bonus=100.0):
        self.got = False
        self.bonus = bonus

    def reset(self, initial_state: GameState=None):
        self.got = initial_state is not None and initial_state.party_size > 0

    def compute(self, prev_state: GameState, current_state: GameState):
        if not self.got and current_state.party_size > prev_state.party_size:
            self.got = True
            reward = self.bonus
            return reward
        return 0.0

class BattleReward(RewardStrategy):
    def __init__(self, damage_scale=5.0, debuff_bonus=0.5, win_bonus=20.0):
        self.damage_scale = damage_scale
        self.debuff_bonus = debuff_bonus
        self.win_bonus = win_bonus

    def compute(self, prev_state: GameState, current_state: GameState):
        if prev_state.in_battle == 0:
            return 0.0

        if current_state.in_battle == 0:
            return self.win_bonus if prev_state.enemy_hp == 0 else 0.0

        same_enemy = (
            current_state.enemy_max_hp > 0
            and prev_state.enemy_max_hp == current_state.enemy_max_hp
        )
        if not same_enemy:
            return 0.0

        reward = 0.0

        if current_state.enemy_hp < prev_state.enemy_hp:
            damage = prev_state.enemy_hp - current_state.enemy_hp
            reward += self.damage_scale * damage / current_state.enemy_max_hp

        return reward
    
class MilestoneReward(RewardStrategy):
    def __init__(self):
        self.stages = [
            ("saiu_casa",     lambda s: s.map_id == 0,                              20.0),
            ("grama_oak",     lambda s: s.map_id == 0 and s.y <= GRASS_TRIGGER_Y and s.x <= GRASS_TRIGGER_X,   30.0),
            ("entrou_lab",    lambda s: s.map_id == 40,                             30.0),
            ("pegou_inicial", lambda s: s.party_size > 0,                          100.0),
            ("saiu_lab",      lambda s: s.map_id == 0 and s.y <= BATTLE_TRIGGER_Y and s.x <= BATTLE_TRIGGER_Y,                              50.0),
            ("route1",        lambda s: s.map_id == 12,                             50.0),
            ("viridian",      lambda s: s.map_id == 1,                             100.0),
        ]
        self.stage = 0

    def reset(self, initial_state=None):
        self.stage = 0
        if initial_state is None:
            return
        
        for i, (_, cond, _) in enumerate(self.stages):
            if cond(initial_state):
                self.stage = i + 1

    def compute(self, prev_state, current_state):
        reward = 0.0
        while self.stage < len(self.stages) and self.stages[self.stage][1](current_state):
            reward += self.stages[self.stage][2]
            self.stage += 1
        return reward