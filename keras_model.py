#Import dependencies 
from riskenv import RiskEnv

import numpy as np

from keras.models import Sequential, Model
from keras.layers import Dense, Activation, Flatten, Embedding, Input, concatenate
from keras.optimizers import Adam

from rl.agents.dqn import DQNAgent
from rl.policy import BoltzmannQPolicy
from rl.memory import SequentialMemory
from rl.processors import MultiInputProcessor, Processor

from riskstate import Phases

env = RiskEnv(n_players=2, random_players=True) 
nb_actions = env.action_space.n
nb_phases = len(Phases)
nb_territories = env.risk.territories.shape[0]

# INPUT_SHAPE = ( 1 + nb_territories * 2 + nb_actions, )
INPUT_SHAPE = ( 1 + nb_territories * 2, )
WINDOW_LENGTH = 1

print(INPUT_SHAPE)

# Initialize environment and extract number of actions 

input_shape = (WINDOW_LENGTH,) + INPUT_SHAPE

inputs = Input(shape=input_shape)
layer1 = Flatten()(inputs)
layer2 = Dense(512, activation="relu")(layer1)
action = Dense(nb_actions, activation="linear")(layer2)

model_final = Model(inputs = inputs, outputs = action)

class MyProcessor(Processor):
    def process_observation(self, observation):
        # return np.append(observation["Phase"], [observation["Owners"].flatten(), observation["Armies"].flatten(), observation["ValidMoves"].flatten()])
        return np.append(observation["Phase"], [observation["Owners"].flatten(), observation["Armies"].flatten()])

    def process_state_batch(self, batch):
        processed_batch = batch.astype('float32') / 255.
        return processed_batch

    def process_reward(self, reward):
        return np.clip(reward, -1., 1.)

memory = SequentialMemory(limit=50000, window_length=WINDOW_LENGTH)
policy = BoltzmannQPolicy()
dqn = DQNAgent(model=model_final, nb_actions=nb_actions, memory=memory, nb_steps_warmup=2000,
               target_model_update=1e-2, policy=policy)
dqn.processor = MyProcessor()
dqn.compile(Adam(lr=1e-1), metrics=['mae'])

dqn.fit(env, nb_steps=int(1e5), visualize=True, verbose=2)