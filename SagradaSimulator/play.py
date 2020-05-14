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

actionsCount = 81

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
model.compile(loss='mae', optimizer=SGD(lr=1e-4), metrics=['mae'])
model.load_weights("weights_new_greedy2.h5")

board = Board([
        [attribute["THREE"], attribute["FOUR"], attribute["ONE"],    attribute["FIVE"],   attribute["ALL"]],
        [attribute["ALL"],   attribute["SIX"],  attribute["TWO"],    attribute["ALL"],    attribute["YELLOW"]],
        [attribute["ALL"],   attribute["ALL"],  attribute["ALL"],    attribute["YELLOW"], attribute["RED"]],
        [attribute["FIVE"],  attribute["ALL"],  attribute["YELLOW"], attribute["RED"],    attribute["SIX"]]
    ], "Zywy ogien")
game = Game(Player("Pawel", board, attribute["RED"]))
# game2 = Game(Player("Bot-v2", copy.deepcopy(board), attribute["RED"]))


def pick_best_possible(prediction, possible_actions):
    prediction = list(prediction[0])
    maxi = [prediction[0], -1]
    for action in possible_actions[1:]:
        if prediction[action] > maxi[0]:
            maxi[0] = prediction[action]
            maxi[1] = action

    return maxi[1] 

print("run")
s1, s2, s3 = game.reset()
s1 = s1.reshape(1, 5, 4, 3)
s2 = s2.reshape(1, 1, -1)
s3 = s3.reshape(1, 1, -1)
game_over = False
points = 0
theoretical_max_score = 0
while game_over == False:
    for dice in game.dices_on_table:
        print(str(dice), end=" ")
    print()
    print(str(game.player.board))
    print(num_to_color[game.player.main_mission_color])
    possible_actions = game.possible_actions()
    #print(possible_actions)
    
    prediction = model.predict([s1, s2, s3])
    # print(prediction)

    c = 0
    for dice in game.dices_on_table:
        if dice.color == game.player.main_mission_color and game.player.move_counter == 0 and c < 2:
            theoretical_max_score += dice.value
            c += 1
    # for a, score in enumerate(prediction[0]):
    #     dice_number = math.floor((a - 1) / (Board.NUMBER_OF_FIELDS))
    #     field_index = (a - 1) % Board.NUMBER_OF_FIELDS
    #     x, y = Board.index_2_xy(field_index)
    #     if dice_number >= len(game.dices_on_table):
    #         continue
    #     dice = game.dices_on_table[dice_number]
    #     print(dice, a, x, y, score)
    action_number = pick_best_possible(prediction, possible_actions)#np.argmax(prediction)
    dice_number = math.floor((action_number - 1) / (Board.NUMBER_OF_FIELDS))
    field_index = (action_number - 1) % Board.NUMBER_OF_FIELDS
    x, y = Board.index_2_xy(field_index)
    dice = game.dices_on_table[dice_number]
    print("PICKED DICE:", action_number, dice_number, str(dice), "x:", str(x), "y:", str(y))
    #print(prediction)
     #pick_best_possible(model.predict(np.array([game._action_out()[0]])), possible_actions)
    # print("network move: ", )
    # dice_number = int(input("Dice number: "))
    # x = int(input("x: "))
    # y = int(input("y: "))
    # game.player.board.put_dice(x, y, game.dices_on_table[dice_number])
    # print((dice_number*20) + Board.xy_2_index(x, y))
    # newS = game.step((dice_number*20) + Board.xy_2_index(x, y))
    newS = game.step(action_number)
    s1 = newS[0][0].reshape(1, 5, 4, 3)
    s2 = newS[0][1].reshape(1, 1, -1)
    s3 = newS[0][2].reshape(1, 1, -1)
    game_over = newS[-2]
    # print(state)
    # points += newS[2]
    #state = game.step(random.randint(-1, 79))
    points += newS[-3]
print(points, theoretical_max_score)
