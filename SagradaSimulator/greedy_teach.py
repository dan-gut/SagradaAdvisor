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
import random
from sklearn.model_selection import train_test_split
import tqdm
from game import Game

gamma = 0.9999
epsilon = 1.0
epsilonMin = 0.01
epsilonDecay = 0.999
actionsCount = 81
# memory = []
# memoryMax = 50000
# it = 0

# Neural Network


board_input = Input(shape=(5, 4, 3), name="board_view")
x = Conv2D(32, (3,3), strides=(1, 1), padding="same", activation="relu")(board_input)
x = Conv2D(32, (3,3), strides=(1, 1), padding="same", activation="relu")(x)

x = Flatten()(x)

dices_input = Input(shape=(1,8), name="dices_view")
y = Dense(128, activation="relu")(dices_input)
y = Dropout(0.3)(y)
y = Dense(128, activation="relu")(y)
y = Dropout(0.3)(y)
y = Dense(128, activation="relu")(y)
y = Dropout(0.3)(y)
y = Flatten()(y)
part1_out = concatenate([x, y])
y = Dense(128, activation="relu")(part1_out)
y = Dropout(0.3)(y)

mission_input = Input(shape=(1,1), name="mission_input")
mission = Flatten()(mission_input)
part2_out = concatenate([y, mission])

z = Dense(128, activation="relu")(part2_out)
z = Dropout(0.3)(z)
main_output = Dense(actionsCount, activation="softmax", name="out")(z)

model = Model(inputs=[board_input, dices_input, mission_input], outputs=main_output)
model.compile(loss='mse', optimizer=Adam(lr=1e-4), metrics=['mae'])
model.summary()
model.load_weights("weights_new_greedy2.h5")

data = []
for i in range(1, 13):
    name = "memory_greedy{}.pkl".format(i)
    data.extend(pickle.load(open(name, 'rb')))
    print("adding {} data".format(i))

random.shuffle(data)

from collections import defaultdict
x_vals = defaultdict(list)
y_vals = []

data_len = len(data)
for i, row in enumerate(data):
    print("{}/{}".format(i, data_len))
    action = row[1]
    x_vals[action].append(row[0])
    # y = np.zeros((1, 81))
    # y[0, action] = 1
    # y_vals.append(y)

def get_y(action):
    y = np.zeros((1, 81))
    y[0, action] = 1
    return y

# X_train, X_test, y_train, y_test = train_test_split(x_vals, y_vals)
epochs_max = min([len(x) for x in x_vals.values()])
for epoch in tqdm.tqdm(range(epochs_max)):
    for action in range(actionsCount):
        model.fit(x_vals[action][epoch], get_y(action), epochs=20, verbose=0)
    if epoch%10 == 0:
        game = Game(Player("Pawel"))
        s1, s2, s3 = game.reset()
        s1 = s1.reshape(1, 5, 4, 3)
        s2 = s2.reshape(1, 1, -1)
        s3 = s3.reshape(1, 1, -1)
        game_over = False
        points = 0
        while game_over == False:
            for dice in game.dices_on_table:
                print(str(dice), end=" ")
            print()
            print(str(game.player.board))
            print(num_to_color[game.player.main_mission_color])
            
            prediction = model.predict([s1, s2, s3])

            action_number = np.argmax(prediction)
            dice_number = math.floor((action_number - 1) / (Board.NUMBER_OF_FIELDS))
            field_index = (action_number - 1) % Board.NUMBER_OF_FIELDS
            x, y = Board.index_2_xy(field_index)
            if dice_number < len(game.dices_on_table):
                dice = game.dices_on_table[dice_number]
                print("PICKED DICE:", action_number, dice_number, str(dice), "x:", str(x), "y:", str(y))
            else:
                print("ILLEGAL DICE:", action_number, "x:", str(x), "y:", str(y))

            newS = game.step(action_number)
            s1 = newS[0][0].reshape(1, 5, 4, 3)
            s2 = newS[0][1].reshape(1, 1, -1)
            s3 = newS[0][2].reshape(1, 1, -1)
            game_over = newS[-2]
            points += newS[-3]
        print("overall_points: ", points)
        with open("out.log", "a+") as f:
            f.write(str(points) + "\n")
        
    # print(state)
    
    #state = game.step(random.randint(-1, 79))
            
        # act = random.randint(0, actionsCount - 1)
        # pos = random.randint(0, len(x_vals[act]) - 1)
        # prediction = model.predict(x_vals[act][pos])
        # print(get_y(action)[0], prediction[0])
        # sums = 0
        # pos_index = -1
        # best_pick_val = max(prediction[0])
        # best_pick = -1
        
        # # best_pick = prediction[0].index(best_pick)
        # for i in range(len(prediction[0])):
        #     sums += abs(prediction[0][i] - get_y(act)[0][i])
        #     if best_pick_val == prediction[0][i]:
        #         best_pick = i
            
        # print("score: ", sums, act, prediction[0][pos_index], best_pick)
        
    if epoch % 50 == 0:
        print("saving...")
        model.save_weights("weights_new_greedy2_1.h5")  
        
# print(y)
# print(model.predict(x))
