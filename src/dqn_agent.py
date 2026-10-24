import random
import numpy as np
from src.actions import Action
from src.q_network import QNetwork
from src.replay_buffer import ReplayBuffer
import torch
import torch.optim as optim

class DQNAgent:

    def __init__(self, state_size, action_size):
        self.q_net = QNetwork(state_size, action_size)
        self.target_net = QNetwork(state_size, action_size)

        self.optimizer = optim.Adam(self.q_net.parameters(), lr=1e-3)

        self.buffer = ReplayBuffer()

        self.gamma = 0.99
        self.epsilon = 1.0
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.05

        self.action_size = action_size

    def act(self, state):
        if np.random.rand() < self.epsilon:
            return np.random.randint(self.action_size)

        state = torch.FloatTensor(state).unsqueeze(0)
        q_values = self.q_net(state)
        return torch.argmax(q_values).item()    

    def decay(self):
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
