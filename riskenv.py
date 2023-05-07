import gymnasium as gym
from gymnasium.spaces import Dict, Discrete, MultiDiscrete, Graph 
from riskstate import *
from maps import default_map
import numpy as np 
import random

class RiskEnv(gym.Env):
    """Custom Environment that follows gym interface."""
    metadata = {"render.modes": ["human"]}

    def __init__(self, n_players=2, random_players = False):
        super().__init__()

        self.risk = new_game(n_players)
        self.observation_unit_max = 10
        self.n_players = n_players
        self.random_players = random_players

        n_territories = self.risk.n_territories()
        self.n_phases = len(Phases)
        self.MAX_ARMIES = 30

        self.action_space = Discrete( n_territories )

        self.observation_space = Dict( {
            "Phase": Discrete(self.n_phases),
            "Territories": MultiDiscrete(np.array([np.array([self.MAX_ARMIES, n_players])]*n_territories))
        } )
        #self.observation_space = MultiDiscrete(np.array([np.array([self.MAX_ARMIES, n_players])]*n_territories))

    def get_observation(self):
        current_phase_index = Phases.index(type(self.risk).__name__)
        obs = {
            "Phase": current_phase_index,
            "Territories": self.risk.territories
        }
        return obs 
        #return self.risk.territories 
        
    
    def get_short_observation(self):
        obs = {} 
        for player in self.risk.active_players:
            obs[f"player_{player}"] = 0
            for country in self.risk.graph:
                if self.risk.territories[country, OWNER] == player:
                    obs[f"player_{player}"] += 1
        return obs, self.risk.turn

    def step(self, action):
        info = {} 
        # Train against random players (agent is at index 0)
        if self.random_players and self.risk.current_player != 0:
            res, state = self.risk.step(random.choice(self.risk.action_space()))
            reward = 0 
        else:
            res, state = self.risk.step(action)
            reward = 1 if self.risk.won else -1 if res.VALID else -5
        self.risk = state
        obs = dict(Phase=np.array[Phases.index(type(self.risk).__name__)], Territories = self.risk.territories)
        return (obs, reward, self.risk.finished() , info)

    def reset(self):
        self.risk = new_game(self.n_players)
        return self.get_observation()
    

    def render(self):
        ...

    def close(self):
        ...