import gym
from riskenv import RiskEnv
from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten
from keras.optimizers import Adam
from rl.agents.dqn import DQNAgent
from rl.policy import EpsGreedyQPolicy
from rl.memory import SequentialMemory

# Define the environment
env = RiskEnv()
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
dqn.fit(env, nb_steps=5000, visualize=False, verbose=2)

# Evaluate the agent
#dqn.test(env, nb_episodes=5, visualize=False)

# import numpy as np 
# from tensorflow.python.keras.models import Sequential
# from tensorflow.python.keras.layers import Dense, Flatten
# from tensorflow.python.keras.optimizer_v1 import Adam
# from riskenv import RiskEnv

# def gather_data(env):
#     min_score = 10
#     sim_steps = 300000
#     trainingX, trainingY = [], []
#     scores = []
#     for _ in range(2):
#         print(f"Starting episode: {_}")
#         observation = env.reset()
#         score = 0
#         training_sampleX, training_sampleY = [], []
#         for step in range(sim_steps):
#             action = np.random.randint(0, 2)
#             one_hot_action = np.zeros(2)
#             one_hot_action[action] = 1
#             training_sampleX.append(observation)
#             training_sampleY.append(one_hot_action)
            
#             observation, reward, done, _ = env.step(action)
#             score += reward
#             if done:
#                 break
#         #if score > min_score:
#         scores.append(score)
#         trainingX += training_sampleX
#         trainingY += training_sampleY
#     trainingX, trainingY = np.array(trainingX), np.array(trainingY)
#     print("Average: {}".format(np.mean(scores)))
#     print("Median: {}".format(np.median(scores)))
#     return trainingX, trainingY

# print("STARTING")

# env = RiskEnv()
# x, y = gather_data(env)
# print(x)
# print(y)

# def build_model(states, actions):
#     model = Sequential()
#     model.add(Flatten(input_shape=(1, states)))
#     model.add(Dense(24, activation="relu"))
#     model.add(Dense(24, activation="relu"))
#     model.add(Dense(actions, activation="linear"))
#     return model 

