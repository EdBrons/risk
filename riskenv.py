import gymnasium as gym
from gymnasium.spaces import Dict, Discrete, MultiDiscrete
from riskstate import *
from maps import default_map

class RiskEnv(gym.Env):
    """Custom Environment that follows gym interface."""

    metadata = {"render.modes": ["human"]}

    def __init__(self, n_players=2):
        super().__init__()
        
        self.risk = new_game(n_players)

        n_territories = self.risk.n_territories()
        n_phases = 9

        self.action_space = Dict( { 
            "Setup": Discrete(n_territories), 
            "Recruitment": Discrete(n_territories),
            "FirstAttack": MultiDiscrete([n_territories, n_territories]),
            "ContinueAttack": Discrete(2),
            "Reinforce": Discrete(2),
            "SubsequentAttack": Discrete(n_territories),
            "Fortify1": Discrete(n_territories),
            "Fortify2": Discrete(n_territories),
            "Fortify3": Discrete(2)
        } )

        self.observation_space = Dict( {
            "Phase": Discrete(n_phases),
            "Territories": MultiDiscrete([n_territories, 2])
        } )

    def get_observation(self):
        return None
    
    def get_reward(self, old_state):
        return 0

    def step(self, action):
        info = {} 
        res, state = self.risk.step(action)
        old_state = self.risk
        self.risk = state
        return self.get_observation(), self.get_reward(old_state), self.risk.finished() , info

    def reset(self):
        ...
        return observation  # reward, done, info can't be included

    def render(self):
        ...

    def close(self):
        ...