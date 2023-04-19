import gymnasium as gym
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

        self.action_space = gym.spaces.Dict( { 
            "Setup": gym.spaces.Discrete(n_territories), 
            "Recruitment": gym.spaces.Discrete(n_territories),
            "FirstAttack": gym.spaces.MultiDiscrete([n_territories, n_territories]),
            "ContinueAttack": gym.spaces.Discrete(2),
            "Reinforce": gym.spaces.Discrete(2),
            "SubsequentAttack": gym.spaces.Discrete(n_territories),
            "Fortify1": gym.spaces.Discrete(n_territories),
            "Fortify2": gym.spaces.Discrete(n_territories),
            "Fortify3": gym.spaces.Discrete(2)
        } )

        self.observation_space = gym.spaces.Dict( {
            "Phase": gym.spaces.Discrete(n_phases),
            "Territories": gym.spaces.MultiDiscrete([n_territories, 2])
        } )

    def get_observation(self):
        return None
    
    def get_reward(self, old_state):
        return 0

    def step(self, action):
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