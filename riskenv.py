import gymnasium as gym
from gymnasium.spaces import Dict, Discrete, MultiDiscrete, Graph 
from riskstate import *
from maps import default_map
import numpy as np 

class RiskEnv(gym.Env):
    """Custom Environment that follows gym interface."""
    metadata = {"render.modes": ["human"]}

    def __init__(self, n_players=2):
        super().__init__()

        self.risk = new_game(n_players)
        self.observation_unit_max = 10
        self.n_players = n_players

        n_territories = self.risk.n_territories()
        self.n_phases = len(Phases)
        self.MAX_ARMIES = 30

        self.action_space = Discrete( n_territories )

        # self.observation_space = Dict( {
        #     #"Graph": Graph(node_space= Discrete(n_territories), edge_space= Discrete(7)),
        #     "Phase": Discrete(self.n_phases),
        #     "Territories": MultiDiscrete(np.array([np.array([self.MAX_ARMIES, n_players])]*n_territories))
        # } )
        self.observation_space = MultiDiscrete(np.array([np.array([self.MAX_ARMIES, n_players])]*n_territories))

    def get_observation(self):
        # current_phase_index = Phases.index(type(self.risk).__name__)
        # return {
        #     #"Graph": self.risk.graph,
        #     "Phase": current_phase_index,
        #     "Territory": np.array([np.array([territory, owner]) for territory, owner in self.risk.territories])
        # }
        return self.risk.territories
    
    def get_short_observation(self):
        obs = {} 
        for player in self.risk.active_players:
            obs[f"player_{player}"] = 0
            for country in self.risk.graph:
                if self.risk.territories[country, OWNER] == player:
                    obs[f"player_{player}"] += 1
        return obs, self.risk.turn

    def step(self, action):
        #TODO: Implement the random player 
        # if self.risk.current_player != 0:
        #     action = np.random.randint(43)
        info = {} 
        res, state = self.risk.step(action)
        #If invalid move
        if res == Move.INVALID:
            self.reward -= 0
        reward = 1 if self.risk.won else -1 if res.VALID else -5
        self.risk = state
        # self.reward += reward 
        return (self.get_observation(), reward, self.risk.finished() , info)

    def reset(self):
        self.risk = new_game(self.n_players)
        self.reward = 0 
        return self.get_observation()
    

    def render(self):
        ...

    def close(self):
        ...