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

class MyProcessor(Processor):
    def process_observation(self, observation):
        return np.append(observation["Phase"], [observation["Owners"].flatten(), observation["Armies"].flatten(), observation["ValidMoves"].flatten()])
        # return np.append(observation["Phase"], [observation["Owners"].flatten(), observation["Armies"].flatten()])

    def process_state_batch(self, batch):
        processed_batch = batch.astype('float32') / 255.
        return processed_batch

    def process_reward(self, reward):
        return np.clip(reward, -1., 1.)

from riskstate import Phases

import datetime

import os
import argparse

parser = argparse.ArgumentParser(
    prog='ModelRunner',
    description='It runs the model and loads it.',
    epilog='Made by Eduardo and Ian')

parser.add_argument('-l', '--load', type=str, default=None)
parser.add_argument('-ll', '--loadlatest', action='store_true')
parser.add_argument('-r', '--train', action='store_true')
parser.add_argument('-t', '--test', action='store_true')
parser.add_argument('--n_players', type=int, default=2)
parser.add_argument('--visualize', action='store_true')
parser.add_argument('-v', '--verbose', type=int, default=0)
parser.add_argument('-s', '--save', action='store_true')
parser.add_argument('-k', '--key', type=str, default='default')
parser.add_argument('--skipsetup', action='store_true')

args = parser.parse_args()

def make_model(in_shape, win_len, nb_actions):
    input_shape = (win_len,) + in_shape
    inputs = Input(shape=input_shape)
    layer1 = Flatten()(inputs)
    layer2 = Dense(512, activation="relu")(layer1)
    layer3 = Dense(512, activation="relu")(layer2)
    layer4 = Dense(512, activation="relu")(layer3)
    action = Dense(nb_actions, activation="linear")(layer4)
    model_final = Model(inputs = inputs, outputs = action)
    return model_final

print(args.skipsetup)

env = RiskEnv(n_players=args.n_players, random_players=True, randomizedSetUp=args.skipsetup) 

def make_agent(model, win_len, nb_actions):
    memory = SequentialMemory(limit=50000, window_length=win_len)
    policy = BoltzmannQPolicy()
    dqn = DQNAgent(model=model, nb_actions=nb_actions, memory=memory, nb_steps_warmup=2000,
                target_model_update=1e-2, policy=policy)
    dqn.processor = MyProcessor()
    return dqn


INPUT_SHAPE = ( 1 + env.risk.n_territories() * 3, )
WINDOW_LENGTH = 1
nb_actions = env.action_space.n

model = make_model(INPUT_SHAPE, WINDOW_LENGTH, nb_actions)
dqn = make_agent(model, WINDOW_LENGTH, nb_actions)
dqn.compile(Adam(lr=1e-1), metrics=['mae'])

if args.loadlatest:
    with open('weights/checkpoint', encoding="utf-8") as f:
        dqn.load_weights('weights/' + f.read().split('"')[1::2][0])
elif args.load is not None:
    dqn.load_weights(args.load)

if args.train:
    dqn.fit(env, nb_steps=int(1e6), visualize=args.visualize, verbose=args.verbose)
elif args.test:
    dqn.test(env, nb_episodes=1, visualize=args.visualize, verbose=args.verbose)

if args.save:
    # dqn.save_weights(f"weights/dqn_weights_{datetime.datetime.now()}.h5f", overwrite=True)
    dqn.save_weights(f"weights/dqn_weights_{args.key}.h5f", overwrite=True)