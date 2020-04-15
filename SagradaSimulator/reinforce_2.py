import numpy as np
# import gym

from keras.models import Sequential, Model
from keras.layers import Dense, Activation, Flatten, Reshape, LSTM, Input
from keras.optimizers import Adam

from rl.agents.dqn import DQNAgent
from rl.agents.sarsa import SARSAAgent
from rl.policy import BoltzmannQPolicy
from rl.memory import SequentialMemory
from game import *


ENV_NAME = 'Sagrada-v0'


# Get the environment and extract the number of actions.
#env = gym.make(ENV_NAME)
#np.random.seed(123)
#env.seed(123)
nb_actions = 801

# Next, we build a very simple model.
# model = Sequential()


# model.add(Flatten(input_shape=(1,145)))
def model_fn(inp):
    board_input = Input(shape=(1, 145), name = "board_view")
    x = Dense(640, activation="relu")(board_input)
    x = Dense(640, activation="relu")(x)
    x = Dense(640, activation="relu")(x)
    main_output = Dense(801, activation="linear", name="out")(x)
    model = Model(inputs=board_input, outputs=main_output)
    print(model_fn.summary())
    return model, inp, main_output


# model.add(Reshape(target_shape=(100, 10)))
# model.add(LSTM(100, return_sequences=True))
# model.add(Reshape(target_shape=(1, 801)))
# model.add(Dense(1600))
# # model.add(Dense(8))
# model.add(Activation('relu'))
# model.add(Dense(nb_actions))
# model.add(Activation('linear'))


Adam._name = "name"

env = Game(Player("Bot"))

# Finally, we configure and compile our agent. You can use every built-in Keras optimizer and
# even the metrics!
memory = SequentialMemory(limit=50000, window_length=1)
policy = BoltzmannQPolicy()

# dqn = SARSAAgent(model=model, nb_actions=nb_actions, nb_steps_warmup=0,
                #  policy=policy)
dqn = DQNAgent(model=model_fn, nb_actions=nb_actions, memory=memory, nb_steps_warmup=100,
             target_model_update=1e-2, policy=policy)
dqn.compile(Adam(lr=1e-3), metrics=['mae'])

# Okay, now it's time to learn something! We visualize the training here for show, but this
# slows down training quite a lot. You can always safely abort the training prematurely using
# Ctrl + C.
dqn.fit(env, nb_steps=50000, visualize=False, verbose=3)

# After training is done, we save the final weights.
dqn.save_weights('dqn_{}_weights.h5f'.format(ENV_NAME), overwrite=True)

# Finally, evaluate our algorithm for 5 episodes.
#dqn.test(env, nb_episodes=5, visualize=True)