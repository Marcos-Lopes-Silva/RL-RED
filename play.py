import os
import time
from pyboy import PyBoy
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv

from src.pokemon_env import PokemonEnv
from src.pyboy_adapter import PyBoyAdapter
from src.pokemon_ram import MemoryService
from src.state_builder import StateBuilder
from src.reward_strategy import RewardSystem

ROM_PATH = "data/red.gb"
MODEL_PATH = "./ppo_pokemon_red.zip"

pyboy_instance = PyBoy(ROM_PATH, window="SDL2")
pyboy_instance.set_emulation_speed(2)

adapter = PyBoyAdapter(pyboy_instance)
memory_service = MemoryService(adapter.pyboy)
state_builder = StateBuilder(memory_service)
reward_system = RewardSystem([])

def make_env():
    return PokemonEnv(adapter, state_builder, reward_system)

env = DummyVecEnv([make_env])

if os.path.exists(MODEL_PATH):
    model = PPO.load(MODEL_PATH, env=env)
    print("Modelo carregado com sucesso!")
else:
    print(f"Erro: Modelo não encontrado em {MODEL_PATH}")
    exit(1)
obs = env.reset()
last_map = None
while True:
    action, _states = model.predict(obs, deterministic=True)
    x, y, map_id, badges, party_size, first_species = state_builder.build()
    obs, reward, done, info = env.step(action)
    print(f"ACTION: {action}")
    print(x, y)

    if done:
        obs = env.reset()
    
    time.sleep(0.01)