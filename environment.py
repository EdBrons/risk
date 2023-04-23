# Risk class
from risk import MAX_ARMIES, OWNER
from risk import RiskState
from risk import AttackRes
from risk import new_game

# Import gym stuff
from gym import Env
from gym.spaces import Dict, Discrete, MultiDiscrete

#Helpers
import numpy as np 
import math 
from enum import Enum, auto 
from maps import default_map

class RiskEnvironment(Env):
    def __init__(self, n_players=2):
        self.risk = new_game(n_players)
        self.initial_state = self.risk
        n_territories = self.risk.n_territories()
        max_borders = self.risk.max_borders()
        self.valid_attacks = 0

        self.reward = 0
        self.turn = 0

        self.action_space = Dict(
            {
            "RECRUIT_PHASE": Discrete(n_territories),                                  #[territory] where to put troops? Only once
            "FIRST_ATTACK": MultiDiscrete([n_territories, n_territories, 2*MAX_ARMIES, MAX_ARMIES]), #[frm, to, how many times?, n_armies]
            "REINFORCE_ATTACK": Discrete(2),                                           #[yes, no]
            "SUBSEQUENT_ATTACK": MultiDiscrete([2, max_borders, 2*MAX_ARMIES]),        #[attack?, to, how many times?] frm is to from FIRST_ATTACK  
            "FORTIFY": MultiDiscrete([n_territories, n_territories, MAX_ARMIES])       #[frm, to, n_armies]
            }
        )
        #Maybe change this
        self.observation_space = MultiDiscrete([n_territories, MAX_ARMIES])

    def step(self, action):
        """return obs, reward, done, truncated, info"""
        
        #One turn of the game 

        #Recruit 
        territory = action["RECRUIT_PHASE"]
        self.risk.recruit(territory) 


        #TODO: TWO things to handle. Invalid move and the players ID 
        #TODO: UPDATE REWARDS. If invalid attack or invalid reinforce give negative reward. 
        frm, to, n_attacks, n_armies = action["FIRST_ATTACK"]
        result = self.risk.attack(frm, to)

        while not self.risk.done and result == AttackRes.UNDECIDED and n_attacks > 0:
            result = self.risk.attack(frm, to)
            if result:
                self.valid_attacks += 1
            n_attacks -= 1
            #TODO: UPDATE REWARD? 
        # If player won
        if result == AttackRes.WON:
            #TODO: UPDATE REWARD 
            if self.risk.done:
                return 
            #If player won it would reinforce
            if action["REINFORCE_ATTACK"] == 0:
                self.risk.reinforce(frm, to, n_armies)
            
            #player could keep attacking 
            frm = to                    #we can only attack from the territory we just conquered
            choice, to, n_attacks = action["SUBSEQUENT_ATTACK"]
            possible_attacks = self.risk.available_attacks(frm)
            if choice == 0 and possible_attacks:             # if wants to attack
                result = self.risk.attack(frm, to)
                while not self.risk.done and result == AttackRes.UNDECIDED and n_attacks > 0:
                    if result:
                        self.valid_attacks += 1
                    result = self.risk.attack(frm, to)
                    n_attacks -= 1
                    #TODO: UPDATE REWARD?
                    if result == AttackRes.WON:
                        #TODO: Update reward 
                        pass
                    if self.risk.done:
                        return 
        #If player lost
        else:
            frm, to, n_armies = action["FORTIFY"]
            self.risk.reinforce(frm, to, n_armies)

        self.risk.current_player = self.risk.get_next_player()
        self.turn += 1
        
        return self.risk.territories, self.reward, self.risk.done

    def get_observation(self):
        obs = {} 
        for player in self.risk.active_players:
            obs[f"player_{player}"] = 0
            for country in self.risk.graph:
                if self.risk.territories[country, OWNER] == player:
                    obs[f"player_{player}"] += 1
        return obs
    
    def reset(self):
        self.risk = self.initial_state
        self.reward = 0
        self.turn = 0 
        pass
        
    def render(self, render_mode = "human"):
        pass 

    




 