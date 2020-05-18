import random
import math
import logging
import numpy as np
from boards import ALL_BOARDS, attribute, num_to_color


class Dice:
    
    def __init__(self, color, value):
        self.color = color  # 7 - 11
        self.value = value  # 1 - 6
    
    def initialize_with_string(self, val):
        data = {"R": 7, "P": 8, "Y": 9, "B":10, "G":11}

        if len(val) != 2:
            return 0
        try:
            self.color = data[val[0]]
            self.value = int(val[1])
        except:
            return -1
        return 1
    @staticmethod
    def get_random_dice(color):
        return Dice(color, random.randint(1, 6))

    def __str__(self):
        return str(num_to_color[self.color]) + str(self.value)
        

class Board:
    BOARD_X_MIN = 0
    BOARD_X_MAX = 4
    BOARD_Y_MIN = 0
    BOARD_Y_MAX = 3
    NUMBER_OF_FIELDS = 20
    '''
    [
     [(0,0), (1,0), (2,0), (3,0), (4,0)],
     [(0,1), (1,1), (2,1), (3,1), (4,1)],
     [(0,2), (1,2), (2,2), (3,2), (4,2)],
     [(0,3), (1,3), (2,3), (3,3), (4,3)]
    ]
    '''
    def __init__(self, board_view, board_name):
        """
        board view: 2D list that consists of BoardElement's, it tells what dice can be placed on which position
        example: [[ALL, ONE, TWO,   THREE, FOUR],
                  [ALL, ONE, GREEN, THREE, FOUR],
                  [ALL, ONE, TWO,   BLUE,  FOUR],
                  [ALL, ONE, TWO,   RED,   FOUR]
                 ]
        board_name: name of the board
        """
        self.board_view = board_view
        self.board_name = board_name
        self.reset()

    def __str__(self):
        ret = ""
        for y in range(Board.BOARD_Y_MAX + 1):
            for x in range(Board.BOARD_X_MAX + 1):
                if self.dices[y][x] == attribute["EMPTY"]:
                    ret += str(num_to_color[self.board_view[y][x]]) + "  "
                else:
                    ret += str(self.dices[y][x]) + " "
            ret += "\n"
        return ret

    @staticmethod
    def index_2_xy(index):
        if index >= Board.NUMBER_OF_FIELDS:
            index %= Board.NUMBER_OF_FIELDS

        x = index % (Board.BOARD_X_MAX + 1)
        y = math.floor(index / (Board.BOARD_X_MAX + 1))
        return x, y

    @staticmethod
    def xy_2_index(x, y):
        return y * (Board.BOARD_X_MAX + 1) + x + 1

    def reset(self):
        self.dices = [
                      [attribute["EMPTY"], attribute["EMPTY"], attribute["EMPTY"], attribute["EMPTY"], attribute["EMPTY"]],
                      [attribute["EMPTY"], attribute["EMPTY"], attribute["EMPTY"], attribute["EMPTY"], attribute["EMPTY"]],
                      [attribute["EMPTY"], attribute["EMPTY"], attribute["EMPTY"], attribute["EMPTY"], attribute["EMPTY"]],
                      [attribute["EMPTY"], attribute["EMPTY"], attribute["EMPTY"], attribute["EMPTY"], attribute["EMPTY"]]
                     ]
        self._no_dices = True

    def put_dice(self, x, y, dice):
        """Should not allow to put dice in incorrect position"""
        if self._can_put_dice(x, y, dice):
            self.dices[y][x] = dice
            self._no_dices = False
            return True
        else:
            return False

    def _can_put_dice(self, x, y, dice):
        """
        1. dice cannot be outside of board
        2. spot must be free and with correct color/value
        3. dice cannot be neighbour with dice with the same color or number
        4. dice must be placed so:
           4a. is neighbour to any dice put already on board (can be askew)
           4b. if there is no dice on board, must be near edge
        """
        #1.
        if x < Board.BOARD_X_MIN or x > Board.BOARD_X_MAX:
            return False
        if y < Board.BOARD_Y_MIN or y > Board.BOARD_Y_MAX:
            return False

        #2.
        if self.dices[y][x] != attribute["EMPTY"]:
            return False
        
        if dice.color != self.board_view[y][x] and \
           dice.value != self.board_view[y][x] and \
           self.board_view[y][x] != attribute["ALL"]:
            return False

        #3.
        if y > Board.BOARD_Y_MIN and self.dices[y - 1][x] != attribute["EMPTY"]:
            if self.dices[y - 1][x].color == dice.color or \
               self.dices[y - 1][x].value == dice.value: 
                return False

        if y < Board.BOARD_Y_MAX and self.dices[y + 1][x] != attribute["EMPTY"]:
            if self.dices[y + 1][x].color == dice.color or \
               self.dices[y + 1][x].value == dice.value: 
                return False
        
        if x > Board.BOARD_X_MIN and self.dices[y][x - 1] != attribute["EMPTY"]:
            if self.dices[y][x - 1].color == dice.color or \
               self.dices[y][x - 1].value == dice.value: 
                return False

        if x < Board.BOARD_X_MAX and self.dices[y][x + 1] != attribute["EMPTY"]:
            if self.dices[y][x + 1].color == dice.color or \
               self.dices[y][x + 1].value == dice.value: 
                return False

        #4b.
        if self._no_dices:
            if (x == Board.BOARD_X_MIN or x == Board.BOARD_X_MAX or \
                y == Board.BOARD_Y_MIN or y == Board.BOARD_Y_MAX):
                return True
            else:
                return False

        #4a.
        delta = [-1, 0, 1]
        for x_delta in delta:
            for y_delta in delta:
                if x == Board.BOARD_X_MIN and x_delta == -1:
                    continue
                if x == Board.BOARD_X_MAX and x_delta == 1:
                    continue
                if y == Board.BOARD_Y_MIN and y_delta == -1:
                    continue
                if y == Board.BOARD_Y_MAX and y_delta == 1:
                    continue

                if self.dices[y + y_delta][x + x_delta] is not attribute["EMPTY"]:
                    return True
        
        return False

    def _get_field_binary_representation(self, x, y):
        """Although field can be represented as dice or requirement for dice, it is much more convenient for outside use
        to represent state of each field on board as number. This not only allows to use required types only inside this
        library but also gives convienience in use because of not requiring knowledge about game.
        Function returns number which represents state of field.
        Each field can have several values depending on board and dice put there:
        - color or value on board picked + "any dice" -> 12 + 1 states = 13 states
        - color of dice 6 states (0 - no dice, 1 - RED, ...)
        - value of dice 7 states (0 - no dice, 1 - 1, ...)
        this together yields 42*13 = 546 different states. To represent them 10 bits will be used.
        _ _ _|_ _ _|_ _ _ _|
        value|color| field |

        """
        if self.dices[y][x] == attribute["EMPTY"]:
            return self.board_view[y][x]
        else:
            return (self.dices[y][x].value << 7 | (self.dices[y][x].color - 6) << 4 | self.board_view[y][x])

    def get_board_state_binary(self):
        ret = []
        for y in range(Board.BOARD_Y_MAX + 1):
            for x in range(Board.BOARD_X_MAX + 1):
                ret.append(self._get_field_binary_representation(x, y))
        return ret

    def _get_field_number_representation(self, x, y):
        pass
        '''
        Field can be represented as one hot, this requires vector of length 7 + 7 + 13. 
        See _get_field_binary_representation for details.
        Returns vector for field with x, y position
        '''
        #ret = [0 for i in range(27)]
        ret = [0, 0, 0]
        if self.dices[y][x] == attribute["EMPTY"]:
            ret[0] = 0
            ret[1] = 0
        else:
            ret[0] = self.dices[y][x].value / 6
            ret[1] = (self.dices[y][x].color - 7) / 5

        ret[2] = self.board_view[y][x] / 13
        return ret

    def get_board_state_number_representation(self):
        ret = []
        for y in range(Board.BOARD_Y_MAX + 1):
            for x in range(Board.BOARD_X_MAX + 1):
                ret.extend(self._get_field_number_representation(x, y))
        return ret

    def _get_field_one_hot_representation(self, x, y):
        pass
        '''
        Field can be represented as one hot, this requires vector of length 7 + 7 + 13. 
        See _get_field_binary_representation for details.
        Returns vector for field with x, y position
        '''
        ret = [0 for i in range(27)]
        if self.dices[y][x] == attribute["EMPTY"]:
            ret[0] = 1
            ret[7] = 1
        else:
            ret[self.dices[y][x].value] = 1
            ret[self.dices[y][x].color + 1] = 1

        ret[self.board_view[y][x] + 14] = 1
        return ret
    
    def get_board_state_one_hot(self):
        ret = []
        for y in range(Board.BOARD_Y_MAX + 1):
            for x in range(Board.BOARD_X_MAX + 1):
                ret.extend(self._get_field_one_hot_representation(x, y))
        return ret


    def get_board_state_for_conv2d(self):
        ret = []
        for y in range(Board.BOARD_Y_MAX + 1):
            for x in range(Board.BOARD_X_MAX + 1):
                ret.append(np.array(self._get_field_number_representation(x, y)))
        return ret


    def get_possible_actions(self, dices):
        actions = [0] #it is always possible to do nothing
        for dice_index, dice in enumerate(dices):
            for x in range(Board.BOARD_X_MAX + 1):
                for y in range(Board.BOARD_Y_MAX + 1):
                    if self._can_put_dice(x, y, dice):
                        actions.append(Board.xy_2_index(x, y) + (20 * dice_index))
                        #print(Board.xy_2_index(x, y), (20 * dice_index))
        return actions


class Player:
    """
    Each player has it's own different color (chosen by random), dices with their color their bord are calculated as
    points to final score.
    Example:
    Player has Purple color
    On his board dice with "6" on it will give him 6 points to final score, dice with "2" -> 2 points
    """
    def __init__(self, name, board=None, main_mission_color=None):
        self.name = name
        self.main_mission_color = None
        self.board = None
        if board is not None:
            self.board = board
        else:
            logging.warning("Default board")
            self.board = ALL_BOARDS["zywy_ogien"]

        if main_mission_color is not None:
            self.main_mission_color = main_mission_color
        else:
            logging.warning("Default mission colour")
            self.main_mission_color = attribute["RED"]
        self.reset()

    def check_params(self):
        if self.main_mission_color not in [attribute['RED'],
                                           attribute['PURPLE'],
                                           attribute['YELLOW'],
                                           attribute['BLUE'],
                                           attribute['GREEN']]:
            raise RuntimeError("main_mission_color must be color!")

    def reset(self):
        self.move_counter = 0
        self.round_counter = 1
        # self.main_mission_color = random.randint(7, 11)
        # key = random.choice(list(ALL_BOARDS.keys())) #list(ALL_BOARDS.keys())[0]#
        # self.board = Board(ALL_BOARDS[key], key)
        # self.board = Board(ALL_BOARDS['ALL'], "ALL")
        self.check_params()

    def calculate_points(self):
        points = 0
        fill_ratio = 20
        #print(str(self.board))
        for x in range(Board.BOARD_X_MAX + 1):
            for y in range(Board.BOARD_Y_MAX + 1):
                if self.board.dices[y][x] == attribute["EMPTY"]:
                    points -= 1.0
                    fill_ratio -= 1
                    continue
                else:
                    points += 1

                if self.board.dices[y][x].color == self.main_mission_color:
                    points += (self.board.dices[y][x].value)
        return points, fill_ratio/20
                

class Game:
    DICES_TO_PICK_BY_PLAYER = 2
    NUMBER_OF_ROUNDS = 10

    def __init__(self, player):
        self.player = player
        self.prepare_game()
        self._dices_to_draw_each_round = 4 # one player
        
    def prepare_game(self):
        self.player.round_counter = 1
        self.player.move_counter = 0
        self._dices_to_draw_from = []
        self.dices_on_table = []
        self._game_finished = False

        for color in range(7, 12):
            for d in range(15):
                self._dices_to_draw_from.append(Dice.get_random_dice(color))
        random.shuffle(self._dices_to_draw_from)

    def toss_random_dices(self, count):
        # self.dices_on_table.append(Dice(attribute["RED"], attribute['SIX']))
        # self.dices_on_table.append(Dice(attribute["RED"], attribute['FIVE']))
        # self.dices_on_table.append(Dice(attribute["BLUE"], attribute['ONE']))
        # self.dices_on_table.append(Dice(attribute["GREEN"], attribute['FOUR']))
        for i in range(count):
            random_index = random.randint(0, len(self._dices_to_draw_from) - 1)
            self.dices_on_table.append(self._dices_to_draw_from.pop(random_index))

    def _get_dice_number_representation(self, dice):
        """One hot vector of 12 values"""
        vec = [0, 0]
        vec[0] = (dice.color - 7)/5
        vec[1] = dice.value / 6
        return vec

    def _get_dice_one_hot(self, dice):
        """One hot vector of 12 values"""
        vec = [0 for i in range(11)]
        vec[dice.color - 1] = 1
        vec[dice.value - 1] = 1
        return vec

    def get_dices_on_table_numbers_representation(self):
        """this will return one hot for each dice on table, to keep one_hot vector the same length
            no matter how many dices on board
            return format:
            - empty -> one on first position
            - bits [1-6] - digits 1 - 6
            - bits [7-11] - colors RED - GREEN
        """
        empty_dice = [0, 0]

        return_vector = []
        for i in range(4):
            if i >= len(self.dices_on_table):
                return_vector.extend(empty_dice)
            else:
                return_vector.extend(self._get_dice_number_representation(self.dices_on_table[i]))
        return return_vector

    def get_dices_on_table_conv2D(self):
        empty_dice = [0, 0]

        return_vector = []
        for i in range(4):
            if i >= len(self.dices_on_table):
                return_vector.append(empty_dice)
            else:
                return_vector.append(self._get_dice_number_representation(self.dices_on_table[i]))
        return return_vector


    def get_dices_on_table_one_hot(self):
        """this will return one hot for each dice on table, to keep one_hot vector the same length
            no matter how many dices on board
            return format:
            - empty -> one on first position
            - bits [1-6] - digits 1 - 6
            - bits [7-11] - colors RED - GREEN
        """
        empty_dice = [0 for i in range(11)]
        empty_dice[0] = 1

        return_vector = []
        for i in range(4):
            if i >= len(self.dices_on_table):
                return_vector.extend(empty_dice)
            else:
                return_vector.extend(self._get_dice_one_hot(self.dices_on_table[i]))
        return return_vector


    def _action_out(self):
        """
        function will return:
            - vector consiting of:
                * dices on table (that were randomly picked) - "one hot",
                * number of dices to pick left (normalized)
                * current player's board state as "one hot" vector
            - player points (normalized) -> assuming max points (15 * 6) + NUMBER_OF_FIELDS
            - bool if game is finished (True == finished)

        *(15 * 6) + Board.NUMBER_OF_FIELDS = 110
        - 15: max number of dices of one color (only one specific color gives points to player)
        - 6: max number of points per dice in proper color
        - NUMBER_OF_FIELDS: "-NUMBER_OF_FIELDS" is minimal number of points if no dices on table.

        In practice this score is not reachable since it means that player during game  got
        15 out of 40 dices in his color and also all of them were "6".
        """

        out_vec = []

        out_vec.append(np.array(self.player.board.get_board_state_for_conv2d()))
        out_vec.append(np.array(self.get_dices_on_table_numbers_representation()))
        mission_color = (self.player.main_mission_color - 7)/5
        out_vec.append(np.array(mission_color))
        
        info = {"None": 0}
        ret = (out_vec,
               self.reward,
               self._game_finished,
               info)

        return ret

    def reset(self):
        self.reward = 0
        self.prepare_game()
        self.player.board.reset()
        self.player.reset()
        self.toss_random_dices(4)
        return self._action_out()

    def possible_actions(self):
        return self.player.board.get_possible_actions(self.dices_on_table)

    def next_round(self):
        self.dices_on_table = []
        self.player.round_counter += 1
        self.player.move_counter %= 2
        self.toss_random_dices(self._dices_to_draw_each_round)

    def step(self, action_number):
        """For one player, he has to pick 2 dices out of four, one step will be to pick dice and put it in correct position
            function return value: see self._action_out(self) function
            action parameter is integer in range [-1, self._dices_to_draw_each_round * Board.NUMBER_OF_FIELDS]
            [0-19] -> dice 0 to field [0-19]
            [20-39] -> dice 1 to field [0-19]
            ...
            0 - No action
            fields are indexed first in x axis then in y axis

            or 0 if no action is performed (skip move)
        """
        # for dice in self.dices_on_table:
        #     print(str(dice), end=" ")
        # print()
        # action_number, dice_number = action

        self.reward = -1
        logging.debug(str(self.player.board) + "\n")
        for dice in self.dices_on_table:
            logging.debug(str(dice))

        logging.debug("\n")
        logging.debug(str(action_number))
        if self.player.round_counter == Game.NUMBER_OF_ROUNDS + 1:
            self._game_finished = True
            # print(str(self.player.board), num_to_color[self.player.main_mission_color], self.player.calculate_points())

            return self._action_out()
        
        #no action
        if action_number == 0:
            self.player.move_counter += 1
            if self.player.move_counter == Game.DICES_TO_PICK_BY_PLAYER:
                self.next_round()
            return self._action_out()

        
        dice_number = math.floor((action_number - 1) / (Board.NUMBER_OF_FIELDS))
        logging.debug("step: dice_number: {}, action_number: {}".format(dice_number, action_number))
        field_index = (action_number - 1) % Board.NUMBER_OF_FIELDS
        # field_index = action_number
        x, y = Board.index_2_xy(field_index)
        
        #illegal action
        if dice_number >= len(self.dices_on_table):
            self.player.move_counter += 1
            if self.player.move_counter == Game.DICES_TO_PICK_BY_PLAYER:
                self.next_round()
            return self._action_out()

        dice = self.dices_on_table[dice_number]
        logging.debug(str(dice) + str(x) + str(y))

        #if wrong action (illegal move) was given, just pretend as -1 action happened
        if not self.player.board._can_put_dice(x, y, dice):
            self.player.move_counter += 1
            # self.player.round_counter += 1
            if self.player.move_counter == Game.DICES_TO_PICK_BY_PLAYER:
               self.next_round()
            return self._action_out()
        
        #proper action
        #print(self.dices_on_table)
        self.player.board.put_dice(x, y, dice)
        if dice.color == self.player.main_mission_color:
            self.reward = dice.value + 1
        else:
            self.reward = 1
        self.player.move_counter += 1
        # self.player.round_counter += 1
        self.dices_on_table.remove(dice)
        if self.player.move_counter == Game.DICES_TO_PICK_BY_PLAYER:
            self.next_round()
        return self._action_out()

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    board = Board([
        [attribute["THREE"], attribute["FOUR"], attribute["ONE"],    attribute["FIVE"],   attribute["ALL"]],
        [attribute["ALL"],   attribute["SIX"],  attribute["TWO"],    attribute["ALL"],    attribute["YELLOW"]],
        [attribute["ALL"],   attribute["ALL"],  attribute["ALL"],    attribute["YELLOW"], attribute["RED"]],
        [attribute["FIVE"],  attribute["ALL"],  attribute["YELLOW"], attribute["RED"],    attribute["SIX"]]

    ], "Zywy ogien")

    game = Game(Player("Pawel", board, attribute["RED"]))
    scores = []
    for i in range(100):
        state = game.reset()
        game_over = state[-1]
        #points = 0
        while game_over == False:
            game_over = state[-2]
            possible_actions = game.possible_actions()
            #print(possible_actions)
            # state = game.step(possible_actions[random.randint(0, len(possible_actions)-1)]) #pick last possible action
            state = game.step(random.randint(0, 801))
            # points += state[-3]
        scores.append(game.player.calculate_points()[0])
    
    print(sum(scores)/ len(scores))
