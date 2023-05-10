import numpy as np
from enum import Enum, auto
from maps import default_map
from riskenv import RiskEnv

Env = RiskEnv(2, randomizedSetUp=True)
for _ in range(100000):    
    Env.render('mode')

# Env.step(0)
# # print(Env.risk.action_space())
# for k, v in Env.get_observation().items():
#     print(k, v.shape)



