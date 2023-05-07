#Import dependencies 
from riskenv import RiskEnv

import numpy as np

from keras.models import Sequential, Model
from keras.layers import Dense, Activation, Flatten, Input, concatenate
from keras.optimizers import Adam

from rl.agents.dqn import DQNAgent
from rl.policy import BoltzmannQPolicy
from rl.memory import SequentialMemory
from rl.processors import MultiInputProcessor


from rl.callbacks import (
    TrainEpisodeLogger,
    TrainIntervalLogger,
    FileLogger
)

# Initialize environment and extract number of actions 
env = RiskEnv(random_players=True) 
nb_actions = env.action_space.n

# Build a model for every element in a our observation space 
model_phase = Sequential()
model_phase.add(Flatten(input_shape=(1,1), name='Phase'))
model_phase_input = Input(shape=(1,1), name='Phase')
model_phase_encoded = model_phase(model_phase_input)

model_territories = Sequential()
model_territories.add(Flatten(input_shape=(1,1), name='Territories'))
model_territories_input = Input(shape=(1,1), name='Territories')
model_territories_encoded = model_territories(model_territories_input)

con = concatenate([model_phase_encoded, model_territories_encoded])

hidden = Dense(16, activation='relu')(con)
for _ in range(2): 
	hidden = Dense(16, activation='relu')(hidden)
output = Dense(nb_actions, activation='linear')(hidden)
model_final = Model(inputs=[model_phase_input, model_territories_input], outputs=output)
model_final.summary()

# Configure and compile our agent
memory = SequentialMemory(limit=50000, window_length=1)
policy = BoltzmannQPolicy()
dqn = DQNAgent(model=model_final, nb_actions=nb_actions, memory=memory, nb_steps_warmup=2000,
               target_model_update=1e-2, policy=policy)
dqn.processor = MultiInputProcessor(2)
dqn.compile(Adam(lr=1e-3), metrics=['mae'])

# Train the agent 
dqn.fit(env, nb_steps=int(1e5), visualize=False, verbose=2)