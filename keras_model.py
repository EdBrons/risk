# #Import dependencies 
# from riskenv import RiskEnv

# import numpy as np

# from keras.models import Sequential, Model
# from keras.layers import Dense, Activation, Flatten, Input, concatenate
# from keras.optimizers import Adam

# from rl.agents.dqn import DQNAgent
# from rl.policy import BoltzmannQPolicy
# from rl.memory import SequentialMemory
# from rl.processors import MultiInputProcessor


# from rl.callbacks import (
#     TrainEpisodeLogger,
#     TrainIntervalLogger,
#     FileLogger
# )

# # Initialize environment and extract number of actions 
# env = RiskEnv(random_players=True) 
# nb_actions = env.action_space.n

# # Build a model for every element in a our observation space 
# model_phase = Sequential()
# model_phase.add(Flatten(input_shape=(1,1), name='Phase'))
# model_phase_input = Input(shape=(1,1), name='Phase')
# model_phase_encoded = model_phase(model_phase_input)

# model_territories = Sequential()
# model_territories.add(Flatten(input_shape=(1,) + env.observation_space["Territories"].shape, name='Territories'))
# model_territories_input = Input(shape=(1, 42, 2), name='Territories')
# model_territories_encoded = model_territories(model_territories_input)

# con = concatenate([model_phase_encoded, model_territories_encoded])

# hidden = Dense(16, activation='relu')(con)
# for _ in range(2): 
# 	hidden = Dense(16, activation='relu')(hidden)
# output = Dense(nb_actions, activation='linear')(hidden)
# model_final = Model(inputs=[model_phase_input, model_territories_input], outputs=output)
# model_final.summary()

# # Configure and compile our agent
# memory = SequentialMemory(limit=50000, window_length=1)
# policy = BoltzmannQPolicy()
# dqn = DQNAgent(model=model_final, nb_actions=nb_actions, memory=memory, nb_steps_warmup=2000,
#                target_model_update=1e-2, policy=policy)
# dqn.processor = MultiInputProcessor(2)
# dqn.compile(Adam(lr=1e-3), metrics=['mae'])

# # Train the agent 
# dqn.fit(env, nb_steps=int(1e5), visualize=False, verbose=2)



from keras.models import Sequential 
from keras.layers import Dense, Activation, Flatten
from keras.optimizers import Adam
from rl.agents.dqn import DQNAgent
from rl.policy import EpsGreedyQPolicy
from rl.memory import SequentialMemory

from riskenv import RiskEnv

env = RiskEnv(random_players=True)
nb_actions = env.action_space.n

# Define the model 

model = Sequential()
model.add(Flatten(input_shape=(1,) + env.observation_space.shape))
model.add(Dense(16))
model.add(Activation('relu'))
model.add(Dense(16))
model.add(Activation('relu'))
model.add(Dense(nb_actions))
model.add(Activation('linear'))

# Define the policy 
policy = EpsGreedyQPolicy()

# Define the memory 
memory = SequentialMemory(limit=50000, window_length=1)

# Define the agent 
dqn = DQNAgent(model=model, nb_actions=nb_actions, memory=memory, nb_steps_warmup=10,
                target_model_update=1e-2, policy=policy)

# Compile the model 
dqn.compile(Adam(lr=1e-3), metrics=['mae'])

# Train the agent 
print("TRAINING")
dqn.fit(env, nb_steps=1000000, visualize=True, verbose=2)

print("DONE TRAINING")
# dqn.test(env, visualize=True, verbose = 2)