import os
from pyboy import PyBoy
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import SubprocVecEnv, VecMonitor
from stable_baselines3.common.callbacks import CheckpointCallback

from src.pokemon_env import PokemonEnv
from src.pyboy_adapter import PyBoyAdapter
from src.pokemon_ram import MemoryService
from src.state_builder import StateBuilder
from src.reward_strategy import RewardSystem, ProgressReward, NoveltyReward, StagnationPenalty, BacktrackPenalty

ROM_PATH = "data/red.gb"
MODEL_PATH = "ppo_pokemon_red"
N_ENVS = 8
TOTAL_TIMESTEPS = 1_000_000


def make_env(rank):
    def _init():
        pyboy = PyBoy(ROM_PATH, window="null")
        pyboy.set_emulation_speed(0)

        adapter = PyBoyAdapter(pyboy)
        memory_service = MemoryService(adapter.pyboy)
        state_builder = StateBuilder(memory_service)

        reward_system = RewardSystem([
            ProgressReward(),
            NoveltyReward(),
            StagnationPenalty(),
            BacktrackPenalty()
        ])

        return PokemonEnv(adapter, state_builder, reward_system)
    return _init


if __name__ == "__main__":
    if not os.path.exists(ROM_PATH):
        print(f"Erro: ROM não encontrada em {ROM_PATH}")
        exit(1)

    env = SubprocVecEnv([make_env(i) for i in range(N_ENVS)])
    env = VecMonitor(env)

    model = PPO(
        "MlpPolicy",
        env,
        verbose=1,
        learning_rate=3e-4,
        n_steps=512,
        batch_size=256,
        n_epochs=10,
        gamma=0.99,
        device="cpu",
        tensorboard_log="./ppo_tensorboard/",
    )

    checkpoint = CheckpointCallback(
        save_freq=50_000 // N_ENVS,
        save_path="./checkpoints/",
        name_prefix="ppo_pokemon",
    )

    print("Iniciando treinamento com PPO...")
    model.learn(total_timesteps=TOTAL_TIMESTEPS, callback=checkpoint)
    model.save(MODEL_PATH)

    print("Treinamento concluído e modelo salvo.")