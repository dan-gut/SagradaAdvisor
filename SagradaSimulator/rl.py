from keras.models import Sequential
from keras.layers import Dense, Activation
from keras.optimizers import SGD, Adadelta, Adam
from game import *
import random
import numpy as np
import logging
logging.getLogger().setLevel(logging.INFO)

gamma = 1.0
epsilon = 1.0
epsilonMin = 0.01
epsilonDecay = 0.999
actionsCount = 80

# Neural Network
model = Sequential()
model.add(Dense(800, input_dim=589, activation='relu'))
model.add(Dense(500, activation='relu'))
model.add(Dense(actionsCount, activation='linear'))
model.compile(loss='mse', optimizer=Adam(), metrics=['mae'])

def train(epochs):
    board = Board([
        [attribute["THREE"], attribute["FOUR"], attribute["ONE"],    attribute["FIVE"],   attribute["ALL"]],
        [attribute["ALL"],   attribute["SIX"],  attribute["TWO"],    attribute["ALL"],    attribute["YELLOW"]],
        [attribute["ALL"],   attribute["ALL"],  attribute["ALL"],    attribute["YELLOW"], attribute["RED"]],
        [attribute["FIVE"],  attribute["ALL"],  attribute["YELLOW"], attribute["RED"],    attribute["SIX"]]
    ], "Zywy ogien")
    game = Game(Player("Pawel", board, attribute["RED"]))

    scores = []
    for epoch in range(epochs):
        r = simulate(game)
        scores.append(r)
        logging.info("epoch: {} score: {} avg_score: {}".format(epoch, r, sum(scores)/(epoch+1)))

def simulate(game):
    global epsilon
    s, r, done = game.reset()
    s = np.array([s])
    
    while done == False:
        #possible_actions = game.possible_actions()
        #state = game.step(possible_actions[-1]) #pick last possible action
        if np.random.rand() <= epsilon:
            possible_actions = game.possible_actions()
            a = possible_actions[random.randint(0, len(possible_actions) - 1)]
            #print("random:", a, possible_actions)
        else:
            a = np.argmax(model.predict(s))
            #print("prediction:", a)
        newS, r, done = game.step(a)
        newS = np.array([newS])
        target = r + gamma * np.max(model.predict(newS))
        target_f = model.predict(s)[0]
        #print(target_f)
        #print(a)
        target_f[a] = target
        model.fit(s, target_f.reshape(-1, actionsCount), epochs=1, verbose=0)
        #memory.append((s, a, r, newS, done))
        s = newS

    #points = state[-2]
    if epsilon > epsilonMin:
        epsilon *= epsilonDecay

    return r

if __name__ == "__main__":
    train(10000)