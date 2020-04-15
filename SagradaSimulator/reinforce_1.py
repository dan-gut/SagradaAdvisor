#from comet_ml import Experiment
from keras.models import Sequential, Model
from keras.layers import Dense, Activation, Flatten, Reshape, LSTM, Input, Conv2D, Conv1D, MaxPooling2D, concatenate, SimpleRNN
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


gamma = 0.99
epsilon = 1.0
epsilonMin = 0.01
epsilonDecay = 0.999
actionsCount = 81

# Neural Network


board_input = Input(shape=(5, 4, 3), name="board_view")
x = Conv2D(32, (3,3), strides=(1, 1), padding="same", activation="relu")(board_input)
x = Conv2D(32, (3,3), strides=(1, 1), padding="same", activation="relu")(x)

x = Flatten()(x)

dices_input = Input(shape=(1,8), name="dices_view")
y = Dense(32, activation="relu")(dices_input)
y = Dense(32, activation="relu")(y)
y = Dense(32, activation="relu")(y)
y = Flatten()(y)
part1_out = concatenate([x, y])
y = Dense(128, activation="relu")(part1_out)


mission_input = Input(shape=(1,1), name="mission_input")
mission = Flatten()(mission_input)
part2_out = concatenate([y, mission])

z = Dense(128, activation="relu")(part2_out)

main_output = Dense(actionsCount, activation="linear", name="out")(z)

model = Model(inputs=[board_input, dices_input, mission_input], outputs=main_output)
model.compile(loss='mae', optimizer=SGD(lr=1e-4), metrics=['mae'])
model.summary()
# Memory (Remember & Replay)
memory = []
batch_size = 64
memoryMax = 50000
it = 0

def train(epochs_start, epochs_end):
    global memory
    global model
    global epsilon
    #memory = pickle.load(open("memory_new_possible.pkl", "rb"))
    # board = Board([
    #     [attribute["THREE"], attribute["FOUR"], attribute["ONE"],    attribute["FIVE"],   attribute["ALL"]],
    #     [attribute["ALL"],   attribute["SIX"],  attribute["TWO"],    attribute["ALL"],    attribute["YELLOW"]],
    #     [attribute["ALL"],   attribute["ALL"],  attribute["ALL"],    attribute["YELLOW"], attribute["RED"]],
    #     [attribute["FIVE"],  attribute["ALL"],  attribute["YELLOW"], attribute["RED"],    attribute["SIX"]]
    # ], "Zywy ogien")
    # game = Game(Player("Pawel", board, attribute["RED"]))
    game = Game(Player("Bot"))
    scores = []
    #f = open(str(time.time()) + "_" + "training.out", "w+")
    try:
        #model.load_weights("weights_new_possible.h5")
        pass
    except:
        logging.warning("No weights for network found!")

    for epoch in range(epochs_start, epochs_end):
        r, l = simulate(game)
        scores.append(r)
        #experiment.log_metrics({"score":r})
        logging.info("epoch: {} score: {} avg_score: {} loss: {}, epsilon: {}".format(epoch, r, sum(scores[-20:])/(20.0), l, epsilon))
        with open("out.log", "a+") as f:
            f.write(str(r) + " " + str(l) + "\n")
        #f.write(str(r) + "\n")
        if epoch%300 == 0:
            pass
            model.save_weights("weights_new_possible.h5")
            pickle.dump(memory, open("memory_new_possible.pkl", "wb"))


    #f.close()
    model.save_weights("weights_new_possible.h5")
        
def pick_best_possible(prediction, possible_actions):
    #return np.argmax(prediction)
    prediction = list(prediction[0])
    maxi = [prediction[0], 0]
    #possible_actions.remove(-1)
    for action in possible_actions:
        #if action == or action == 80:
        #    raise RuntimeError("Action inproper", action)
        if prediction[action] > maxi[0]:
            maxi[0] = prediction[action]
            maxi[1] = action
    # with open("picks.hist", "a+") as f:
    #     f.write(str(maxi[0]) + " " + str(maxi[1]) + "\n")
    return maxi[1]

loss = [0 for i in range(actionsCount)]

def simulate(game):
    global epsilon
    global memory
    global model
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
        possible_actions = game.possible_actions()
        #print(possible_actions)
        rnd = False
        if np.random.rand() <= epsilon:
            #possible_actions = possible_actions
            #a = possible_actions[random.randint(0, len(possible_actions) - 1)]
            a = random.randint(0, actionsCount - 1)
            rnd = True
            # print("random:", a, possible_actions)
        else:
            prediction = model.predict([s1, s2, s3])
            #a = pick_best_possible(prediction, possible_actions)
            a = np.argmax(prediction)
            #print("prediction:", a)

        
        c = 0
        for dice in game.dices_on_table:
            if dice.color == game.player.main_mission_color and game.player.move_counter == 0 and c < 2:
                theoretical_max_score += dice.value
                c += 1
            
        newS, r, done, _ = game.step(a)
        #print(str(game.player.board), r, game.player.round_counter)
        print("{}, {}, {}, {}".format(a, rnd, r, game.player.round_counter))
        
        new_s1 = newS[0].reshape(1, 5, 4, 3)
        new_s2 = newS[1].reshape(1, 1, -1)
        new_s3 = newS[2].reshape(1, 1, -1)
        #target = r + gamma * model.predict(newS)[0][]
        memory.append(([s1, s2, s3], a, r, [new_s1, new_s2, new_s3], done))
        s1 = new_s1
        s2 = new_s2
        s3 = new_s3
        score += r

        it += 1
        if it % 4 == 0:
            replay_memory()
        if len(memory)>=memoryMax:
            memory.sort(key=lambda x: x[2], reverse=True)
            memory = memory[:45000]

        if epsilon > epsilonMin:
            epsilon *= epsilonDecay
    print(str(game.player.board), game.player.main_mission_color, round(score, 0), game.player.calculate_points(), theoretical_max_score)
    return round(score, 2), sum([abs(l) for l in loss])

def replay_memory():
    global loss
    # Replay memory
    if len(memory) > batch_size:
        # batch = random.sample(memory, batch_size * 5)
        #for i in range(5):
        #    minibatch = batch[i*batch_size:(i+1) * batch_size]

        buffer = sorted(memory, key=lambda replay: replay[2], reverse=True)
        p = np.array([0.99 ** i for i in range(len(buffer))])
        #print(p)
        p = p / sum(p)
        sample_idxs = np.random.choice(np.arange(len(buffer)),size=batch_size, p=p)
        sample_output = [buffer[idx] for idx in sample_idxs]
        minibatch = np.reshape(sample_output,(batch_size,-1))
        #minibatch = random.sample(memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = 0 
            # print(next_state)
            if not done:
                prediction = model.predict(next_state)
                #print(prediction)
                target = reward + gamma * prediction[0][action]#pick_best_possible(model.predict(next_state), m_game.possible_actions())
            
            #while loss > 1.0:
            one_hot_score = np.zeros((1, actionsCount))
            one_hot_score[0][action] = target
            hist = model.fit(state, one_hot_score.reshape(1,-1), epochs=1, verbose=0)
            loss[action] = hist.history['loss'][-1]

    


if __name__ == "__main__":
    train(0, 100000)
    