from abc import ABC, abstractmethod
import math
from collections import defaultdict
from src.game_state import GameState


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
            reward += 50.0
        return reward


class NoveltyReward(RewardStrategy):
    def __init__(self):
        self.visited = set()

    def reset(self, initial_state=None):
        self.visited.clear()
        if initial_state is not None:
            self.visited.add((initial_state.map_id, initial_state.x, initial_state.y))


    def compute(self, prev_state: GameState, current_state: GameState):
        key = (current_state.map_id, current_state.x, current_state.y)
        if key in self.visited:
            return 0.0
        self.visited.add(key)
        return 0.35


class StagnationPenalty(RewardStrategy):
    def compute(self, prev_state: GameState, current_state: GameState):
        if prev_state.position() == current_state.position():
            return -0.05
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
    def __init__(self, window=100, penalty=-5.0):
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