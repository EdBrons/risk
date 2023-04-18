# Risk class
import risk
from risk import Risk
from risk import Phase

# Import gym stuff
from gym import Env
from gym.spaces import Dict, Discrete, MultiDiscrete

#Helpers
import numpy as np 
import math 
from enum import Enum, auto 
from maps import default_map

class RiskEnvironment(Env):
    def __init__(self, n_players):
        super().__init__()(self)
        self.risk = Risk(n_players)

        self.action_space = Dict(
            {
            "CHOOSE_TERRITORY": Discrete(len(self.risk.graph.keys())), 
            "RECRUITMENT": Discrete(len(self.risk.graph.keys())),
            "FIRST_ATTACK": Discrete(1 + self.risk.get_vertices_count()), # 1 + because there needs to be an option not to attack
            "CONTINUE_ATTACK": Discrete(2),
            "SUBS_ATTACK": Discrete(1 + max([len(verts) for _, verts in self.risk.graph])), 
            "REINFORCE_ATTACK": Discrete(2),
            "FORTIFY":  Discrete(1 + self.risk.get_vertices_count())
            }
            )
        self.observation_space = MultiDiscrete([50]*self.risk.get_vertices_count())

    def step(self, action):
        """return obs, reward, done, truncated, info"""
        pass

    def render(self, render_mode = "human"):
        pass 

    def reset(self):
        pass 




 