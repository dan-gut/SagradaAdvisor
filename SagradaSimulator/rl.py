from keras.models import Sequential
from keras.layers import Dense, Activation
from keras.optimizers import SGD, Adadelta, Adam
from game import *
import random
import time 
import numpy as np
import logging
logging.getLogger().setLevel(logging.INFO)
import copy


gamma = 0.999
epsilon = 1
epsilonMin = 0.1
epsilonDecay = 0.999
actionsCount = 80

# Neural Network
model = Sequential()
model.add(Dense(600, input_dim=589, activation='relu'))
model.add(Dense(800, activation='relu'))
model.add(Dense(300, activation='relu'))
model.add(Dense(actionsCount, activation='linear'))
model.compile(loss='mse', optimizer=Adam(), metrics=['mae'])

# Memory (Remember & Replay)
memory = []
batch_size = 64
memoryMax = 50000

def train(epochs):
    global memory
    global model
    board = Board([
        [attribute["THREE"], attribute["FOUR"], attribute["ONE"],    attribute["FIVE"],   attribute["ALL"]],
        [attribute["ALL"],   attribute["SIX"],  attribute["TWO"],    attribute["ALL"],    attribute["YELLOW"]],
        [attribute["ALL"],   attribute["ALL"],  attribute["ALL"],    attribute["YELLOW"], attribute["RED"]],
        [attribute["FIVE"],  attribute["ALL"],  attribute["YELLOW"], attribute["RED"],    attribute["SIX"]]
    ], "Zywy ogien")
    game = Game(Player("Pawel", board, attribute["RED"]))

    scores = []
    f = open(str(time.time()) + "_" + "training.out", "w+")
    try:
        model.load_weights("weights.h5")
    except:
        logging.warning("No weights for network found!")

    for epoch in range(epochs):
        r = simulate(game)
        scores.append(r)
        logging.info("epoch: {} score: {} avg_score: {}".format(epoch, r, sum(scores[-20:])/(20.0)))
        f.write(str(r) + "\n")
        if epoch%1000 == 0:
            model.save_weights("weights.h5")

    f.close()
    model.save_weights("weights.h5")
        
def pick_best_possible(prediction, possible_actions):
    prediction = list(prediction[0])
    maxi = [prediction[0], -1]
    for action in possible_actions[1:]:
        if prediction[action] > maxi[0]:
            maxi[0] = prediction[action]
            maxi[1] = action

    return maxi[1]

def simulate(game):
    global epsilon
    global memory
    global model
    s, r, done = game.reset()
    s = np.array([s])
    
    while done == False:
        possible_actions = game.possible_actions()
        #state = game.step(possible_actions[-1]) #pick last possible action
        if np.random.rand() <= epsilon:
            #possible_actions = possible_actions
            a = possible_actions[random.randint(0, len(possible_actions) - 1)]
            #print("random:", a, possible_actions)
        else:
            a = pick_best_possible(model.predict(s), possible_actions)
            #a = np.argmax(model.predict(s))
            #print("prediction:", a)
        newS, r, done = game.step(a)
        newS = np.array([newS])
        target = r + gamma * pick_best_possible(model.predict(newS), game.possible_actions())
        target_f = model.predict(s)[0]
        #print(target_f)
        #print(a)
        target_f[a] = target
        model.fit(s, target_f.reshape(-1, actionsCount), epochs=1, verbose=0)
        # if r > 0.1:
        memory.append((copy.deepcopy(game), s, a, r, newS, done))
        s = newS

        if len(memory)==memoryMax:
            #memory.sort(key=lambda x:x[2], reverse=False)
            del memory[:5000]


    #points = state[-2]
    if epsilon > epsilonMin:
        epsilon *= epsilonDecay

    # Replay memory
    if len(memory) > batch_size:
        minibatch = random.sample(memory, batch_size)
        for game, state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = reward + gamma * pick_best_possible(model.predict(next_state), game.possible_actions())

            target_f = model.predict(state)[0]
            target_f[action] = target
            model.fit(state, target_f.reshape(-1, actionsCount), epochs=1, verbose=0)

    return r


if __name__ == "__main__":
    train(100000)