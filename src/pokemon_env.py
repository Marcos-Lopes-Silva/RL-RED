import gymnasium as gym
from gymnasium import spaces
import numpy as np
from src.game_state import GameState
from src.pyboy_adapter import PyBoyAdapter
from src.reward_strategy import RewardSystem
from src.state_builder import StateBuilder

class PokemonEnv(gym.Env):
    def __init__(self, pyboy_adapter: PyBoyAdapter, state_builder: StateBuilder, reward_system: RewardSystem):
        super().__init__()
        self.adapter = pyboy_adapter
        self.state_builder = state_builder
        self.reward_system = reward_system

        self.max_steps = 2048
        self.step_count = 0

        self.prev_state = None
        
        self.observation_space = spaces.Box(low=0, high=1, shape=(4,), dtype=np.float32)
        
        self.action_space = spaces.Discrete(8)
        self.visits = {}
        self.last_action = 0
        self.stuck_steps = 0
        self.observation_space = spaces.Box(low=0, high=1, shape=(18,), dtype=np.float32)

    def _build_obs(self, raw):
        x, y, map_id, badges = raw[0], raw[1], raw[2], raw[3]

        def v(px, py):
            return min(self.visits.get((map_id, px, py), 0), 10) / 10.0

        base = [x / 255.0, y / 255.0, map_id / 255.0, badges / 8.0]
        cur = [v(x, y)]
        neighbors = [v(x, y - 1), v(x, y + 1), v(x - 1, y), v(x + 1, y)]
        stuck = [min(self.stuck_steps, 20) / 20.0]
        last = np.zeros(8, dtype=np.float32)
        last[self.last_action] = 1.0

        return np.array(base + cur + neighbors + stuck + list(last), dtype=np.float32)

    def reset(self, seed=None):
        super().reset(seed=seed)
        self.step_count = 0
        self.visits.clear()
        self.stuck_steps = 0
        self.last_action = 0
        
        self.adapter.pyboy.load_state(open("data/re.state", "rb")) 

        raw_state = self.state_builder.build()
        self.prev_state = self._to_game_state(raw_state)
        self.reward_system.reset(self.prev_state)
        
        observation = self._build_obs(raw_state)
        info = {}
        
        return observation, info

    def step(self, action):
        self.adapter.step(action)
        self.step_count += 1

        raw_state = self.state_builder.build()
        current_game_state = self._to_game_state(raw_state)

        if current_game_state.position() == self.prev_state.position():
            self.stuck_steps += 1
        else:
            self.stuck_steps = 0

        key = (raw_state[2], raw_state[0], raw_state[1])
        self.visits[key] = self.visits.get(key, 0) + 1
        self.last_action = int(action)

        reward = self.reward_system.compute(self.prev_state, current_game_state)
        self.prev_state = current_game_state

        terminated = False 
        truncated = self.step_count >= self.max_steps
        
        observation = self._build_obs(raw_state)
        info = {}

        return observation, reward, terminated, truncated, info

    def _to_game_state(self, raw):
        return GameState(x=raw[0], y=raw[1], map_id=raw[2], badges=raw[3])
