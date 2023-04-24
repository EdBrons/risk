from gymnasium import Env
from gymnasium.spaces import Discrete, MultiDiscrete
from risk import RiskState, MAX_ARMIES
from risk import new_game
from risk import AttackRes



import numpy as np 

class RecruitmentEnv(Env):
    def __init__(self, risk: RiskState):
        
        self.risk = risk
        self.reward = 0 
        n_territories = self.risk.n_territories()
        self.n_players = len(self.risk.active_players)
        self.done = self.risk.done

        self.action_space = MultiDiscrete([n_territories, n_territories])  #[frm, to]
        self.observation_space = MultiDiscrete(np.array([np.array([MAX_ARMIES, self.n_players])]*n_territories))

    def step(self, action):
        """
        return obs, reward, done, truncated, info 
        """
        frm, to = action 
        res = self.risk.attack(frm, to)

        if res == AttackRes.WON:
            self.reward += 1 
        elif res == AttackRes.FAILED:
            self.reward -= 1
        #If invalid 
        elif res == False: 
            self.reward -= 1

        self.done = self.risk.done 
        
        obs = np.array([np.array([territory, owner]) for territory, owner in self.risk.territories])
        return obs, self.reward, self.done, False, {} 

    def reset(self):
        self.risk = new_game(self.n_players)
        self.reward = 0 

    def render(self):
        pass 

    



