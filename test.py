import numpy as np
from enum import Enum, auto
from maps import default_map
from riskenv import RiskEnv

Env = RiskEnv(2)
Env.risk 
# print(Env.reset())
# print(Env.get_observation())

Env.step(0)
# print(Env.risk.action_space())
for k, v in Env.get_observation().items():
    print(k, v.shape)