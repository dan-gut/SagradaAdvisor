#from comet_ml import Experiment
from keras.models import Sequential, Model
from keras.layers import Dense, Activation, Flatten, Reshape, LSTM, Input, Conv2D, Conv1D, MaxPooling2D, concatenate, SimpleRNN, Dropout
from keras.optimizers import SGD, Adadelta, Adam
from keras.callbacks import EarlyStopping
from game import *
import random
import time 
import numpy as np
import logging
logging.getLogger().setLevel(logging.INFO)
import copy
import pickle
import sys

gamma = 0.9999
epsilon = 1.0
epsilonMin = 0.01
epsilonDecay = 0.999
actionsCount = 81
memory = []
memoryMax = 50000
it = 0

def train(epochs_start, epochs_end):
    global memory
    global model
    global epsilon
    game = Game(Player("Bot"))
    scores = []

    for epoch in range(epochs_start, epochs_end):
        r, l = simulate(game)
        scores.append(r)
        #experiment.log_metrics({"score":r})
        logging.info("epoch: {} score: {} avg_score: {} loss: {}, epsilon: {}".format(epoch, r, sum(scores[-20:])/(20.0), l, epsilon))
        with open("out.log", "a+") as f:
            f.write(str(r) + " " + str(l) + "\n")
        
        if epoch % 1000 == 0:
            pickle.dump(memory, open("memory_greedy{}.pkl".format(sys.argv[1]), 'wb'))

def pick_best_action_greedy(game):
    maxi = [-1, 0]
    for i in range(actionsCount):
        game_cp = copy.deepcopy(game)
        _, r, _, _ = game_cp.step(i)
        if r > maxi[0]:
            maxi[0] = r
            maxi[1] = i
        
    return maxi[1]

loss = [0 for i in range(actionsCount)]

def simulate(game):
    global it
    global loss
    s1, s2, s3 = game.reset()
    s1 = s1.reshape(1, 5, 4, 3)
    s2 = s2.reshape(1, 1, -1)
    s3 = s3.reshape(1, 1, -1)
    for dice in game.dices_on_table:
        print(str(dice), end=" ")
    print()
    print(str(game.player.board), game.player.main_mission_color)
    
    score = 0
    theoretical_max_score = 0
    done = False
    while done == False:
        a = pick_best_action_greedy(game)
        newS, r, done, _ = game.step(a)
        # print()
        # print("s1:", s1, "s2:", s2, "s3:", s3)
        # print()
        # print("newS:", newS, r, done)
        # exit(0)
        new_s1 = newS[0].reshape(1, 5, 4, 3)
        new_s2 = newS[1].reshape(1, 1, -1)
        new_s3 = newS[2].reshape(1, 1, -1)
        #target = r + gamma * model.predict(newS)[0][]
        memory.append(([s1, s2, s3], a, r, [new_s1, new_s2, new_s3], done))
        s1 = new_s1
        s2 = new_s2
        s3 = new_s3
        #print(str(game.player.board), r, game.player.round_counter)
        # print("{}, {}, {}".format(a, r, game.player.round_counter))
        score += r
        it += 1
        
    print(str(game.player.board), game.player.main_mission_color, round(score, 0), game.player.calculate_points(), theoretical_max_score)
    return round(score, 2), sum([abs(l) for l in loss])

if __name__ == "__main__":
    train(0, 100000)
    