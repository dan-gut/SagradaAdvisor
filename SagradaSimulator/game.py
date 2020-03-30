import random
import math
import logging

'''
#     We have 13 possible states on board
#     0: everything can be placed there (grey)
#     1 - 6: like numbers on dice
#     colors: RED, PURPLE, YELLOW, RED, BLUE, GREEN
#     empty: 12
#     '''

attribute = {
    "ALL"    :   0,
    "ONE"    :   1,
    "TWO"    :   2,
    "THREE"  :   3,
    "FOUR"   :   4,
    "FIVE"   :   5,
    "SIX"    :   6,

    "RED"    :   7, #1
    "PURPLE" :   8, #2
    "YELLOW" :   9, #3
    "BLUE"   :  10, #4
    "GREEN"  :  11, #5

    "EMPTY"  :  12,
}

num_to_color = {7 : "R", 8: "P", 9:"Y", 10:"B", 11:"G"}

class Dice:
    
    def __init__(self, color, value):
        self.color = color #7 - 11
        self.value = value #1 - 6
    
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
        '''
        board view: 2D list that consists of BoardElement's, it tells what dice can be placed on which position
        example: [[ALL, ONE, TWO,   THREE, FOUR],
                  [ALL, ONE, GREEN, THREE, FOUR],
                  [ALL, ONE, TWO,   BLUE,  FOUR],
                  [ALL, ONE, TWO,   RED,   FOUR]
                 ]
        board_name: name of the board
        '''
        self.board_view = board_view
        self.board_name = board_name
        self.reset()

    def __str__(self):
        ret = ""
        for y in range(Board.BOARD_Y_MAX + 1):
            for x in range(Board.BOARD_X_MAX + 1):
                ret += str(self.dices[y][x]) + " "
            ret += "\n"
        return ret
        #for dice in self.dices:


    @staticmethod
    def index_2_xy(index):
        if index >= Board.NUMBER_OF_FIELDS:
            index %= Board.NUMBER_OF_FIELDS

        x = index % (Board.BOARD_X_MAX + 1)
        y = math.floor(index / (Board.BOARD_X_MAX + 1))
        return x, y

    @staticmethod
    def xy_2_index(x, y):
        return y * (Board.BOARD_X_MAX + 1) + x

    def reset(self):
        self.dices = [
                      [attribute["EMPTY"], attribute["EMPTY"], attribute["EMPTY"], attribute["EMPTY"], attribute["EMPTY"]],
                      [attribute["EMPTY"], attribute["EMPTY"], attribute["EMPTY"], attribute["EMPTY"], attribute["EMPTY"]],
                      [attribute["EMPTY"], attribute["EMPTY"], attribute["EMPTY"], attribute["EMPTY"], attribute["EMPTY"]],
                      [attribute["EMPTY"], attribute["EMPTY"], attribute["EMPTY"], attribute["EMPTY"], attribute["EMPTY"]]
                     ]
        self._no_dices = True

    def put_dice(self, x, y, dice):
        '''Should not allow to put dice in incorrect position'''
        if self._can_put_dice(x, y, dice):
            self.dices[y][x] = dice
            self._no_dices = False
            return True
        else:
            return False

    def _can_put_dice(self, x, y, dice):
        '''
        1. dice cannot be outside of board
        2. spot must be free and with correct color/value
        3. dice cannot be neighbour with dice with the same color or number
        4. dice must be placed so:
           4a. is neighbour to any dice put already on board (can be askew) 
           4b. if there is no dice on board, must be near edge
        '''
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
        '''Although field can be represented as dice or requirement for dice, it is much more convenient for outside use
        to represent state of each field on board as number. This not only allows to use required types only inside this library
        but also gives convienience in use because of not requiring knowledge about game. 
        Function returns number which represents state of field.
        Each field can have several values depending on board and dice put there:
        - color or value on board picked + "any dice" -> 12 + 1 states = 13 states
        - color of dice 6 states (0 - no dice, 1 - RED, ...)
        - value of dice 7 states (0 - no dice, 1 - 1, ...)
        this together yields 42*13 = 546 different states. To represent them 10 bits will be used.
        _ _ _|_ _ _|_ _ _ _|
        value|color| field |
        
        '''
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

    def _get_field_one_hot_representation(self, x, y):
        pass
        '''
        Field can be represented as one hot, this requires vector of length 7 + 7 + 13. See _get_field_binary_representation for details.
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

    def get_possible_actions(self, dices):
        actions = [-1] #it is always possible to do nothing
        for dice_index, dice in enumerate(dices):
            for x in range(Board.BOARD_X_MAX + 1):
                for y in range(Board.BOARD_Y_MAX + 1):
                    if self._can_put_dice(x, y, dice):
                        actions.append(Board.xy_2_index(x, y) + (20 * dice_index))
                        #print(Board.xy_2_index(x, y), (20 * dice_index))
        return actions

class Player:
    '''
    Each player has it's own different color (chosen by random), dices with their color their bord are calculated as points to final score.
    Example:
    Player has Purple color
    On his board dice with "6" on it will give him 6 points to final score, dice with "2" -> 2 points
    '''
    def __init__(self, name, board, main_mission_color):
        self.name = name
        self.board = board
        self.main_mission_color = main_mission_color
        self.move_counter = 0
        self.check_params()

    def check_params(self):
        if self.main_mission_color not in [attribute['RED'], \
                                           attribute['PURPLE'], \
                                           attribute['YELLOW'], \
                                           attribute['BLUE'], \
                                           attribute['GREEN']]:
            raise RuntimeError("main_mission_color must be color!")

    def reset(self):
        self.move_counter = 0

    def calculate_points(self):
        points = 0
        for x in range(Board.BOARD_X_MAX + 1):
            for y in range(Board.BOARD_Y_MAX + 1):
                if self.board.dices[y][x] == attribute["EMPTY"]:
                    points -= 1
                    continue

                if self.board.dices[y][x].color == self.main_mission_color:
                    points += self.board.dices[y][x].value
        return points
                

class Game:
    DICES_TO_PICK_BY_PLAYER = 2
    NUMBER_OF_ROUNDS = 10

    def __init__(self, player):
        self.player = player
        self.prepare_game()
        self._dices_to_draw_each_round = 4 # one player
        
    def prepare_game(self):
        self.round = 1
        self._dices_to_draw_from = []
        self.dices_on_table = []
        self._game_finished = False

        for color in range(7, 12):
            for d in range(15):
                self._dices_to_draw_from.append(Dice.get_random_dice(color))
        
    def toss_random_dices(self, count):
        # self.dices_on_table.append(Dice(attribute["RED"], attribute['SIX']))
        # self.dices_on_table.append(Dice(attribute["RED"], attribute['FIVE']))
        # self.dices_on_table.append(Dice(attribute["BLUE"], attribute['ONE']))
        # self.dices_on_table.append(Dice(attribute["GREEN"], attribute['FOUR']))
        for i in range(count):
            random_index = random.randint(0, len(self._dices_to_draw_from) - 1)
            self.dices_on_table.append(self._dices_to_draw_from.pop(random_index))

    def _get_dice_one_hot(self, dice):
        '''One hot vector of 12 values'''
        vec = [0 for i in range(12)]
        vec[dice.color] = 1
        vec[dice.value] = 1
        return vec

    def get_dices_on_table_one_hot(self):
        '''this will return one hot for each dice on table, to keep one_hot vector the same lenght
            no matter how many dices on board
            return format:
            - empty -> one on first position
            - bits [1-6] - digits 1 - 6
            - bits [7-11] - colors RED - GREEN
        '''
        empty_dice = [0 for i in range(12)]
        empty_dice[0] = 1

        return_vector = []
        for i in range(4):
            if i >= len(self.dices_on_table):
                return_vector.extend(empty_dice)
            else:
                return_vector.extend(self._get_dice_one_hot(self.dices_on_table[i]))
        return return_vector


    def _action_out(self):
        '''
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
        '''
        out_vec = []
        board_state = self.player.board.get_board_state_one_hot()
        assert(len(board_state) == 540)
        
        dices_table = self.get_dices_on_table_one_hot()
        assert(len(dices_table) == 48)

        dices_to_pick = (Game.DICES_TO_PICK_BY_PLAYER - self.player.move_counter) / 2

        out_vec.extend(board_state)
        out_vec.extend(dices_table)
        out_vec.append(dices_to_pick)
        
        normalized_points = (self.player.calculate_points() + Board.NUMBER_OF_FIELDS) / 110.0
        
        return (
                out_vec,
                normalized_points,
                self._game_finished
                )

    def reset(self):
        self.prepare_game()
        self.player.board.reset()
        self.player.reset()
        self.toss_random_dices(self._dices_to_draw_each_round)
        return self._action_out()

    def possible_actions(self):
        return self.player.board.get_possible_actions(self.dices_on_table)

    def next_round(self):
        self.dices_on_table = []
        self.round += 1
        self.player.move_counter %= 2
        self.toss_random_dices(self._dices_to_draw_each_round)

    def step(self, action_number):
        '''For one player, he has to pick 2 dices out of four, one step will be to pick dice and put it in correct position
            function return value: see self._action_out(self) function
            action parameter is integer in range [-1, self._dices_to_draw_each_round * Board.NUMBER_OF_FIELDS]
            [0-19] -> dice 0 to field [0-19]
            [20-39] -> dice 1 to field [0-19]
            ...
            -1 - No action
            fields are indexed first in x axis then in y axis
            
            or -1 if no action is performed (skip move)
        '''
        logging.debug(str(self.player.board) + "\n")
        for dice in self.dices_on_table:
            logging.debug(str(dice))

        logging.debug("\n")
        logging.debug(str(action_number))
        #print(self.round)
        if self.round == Game.NUMBER_OF_ROUNDS:
            self._game_finished = True
            return self._action_out()
        

        #no action
        if action_number == -1:
            self.player.move_counter += 1
            if self.player.move_counter == Game.DICES_TO_PICK_BY_PLAYER:
                self.next_round()
            return self._action_out()

        
        dice_number = math.floor(action_number / Board.NUMBER_OF_FIELDS)
        logging.debug("step: dice_number: {}, action_number: {}".format(dice_number, action_number))
        #print(dice_number)
        field_index = action_number % Board.NUMBER_OF_FIELDS
        x, y = Board.index_2_xy(field_index)
        
        
        #illegal action
        if dice_number == len(self.dices_on_table):
            self.player.move_counter += 1
            if self.player.move_counter == Game.DICES_TO_PICK_BY_PLAYER:
                self.next_round()
            return self._action_out()

        dice = self.dices_on_table[dice_number]
        logging.debug(str(dice) + str(x) + str(y))

        #if wrong action (illegal move) was given, just pretend as -1 action happened
        if not self.player.board._can_put_dice(x, y, dice):
            self.player.move_counter += 1
            if self.player.move_counter == Game.DICES_TO_PICK_BY_PLAYER:
                self.next_round()
            return self._action_out()
        
        #proper action
        #print(self.dices_on_table)
        self.player.board.put_dice(x, y, dice)
        self.player.move_counter += 1
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
    for i in range(1000):
        state = game.reset()
        game_over = state[-1]
        while game_over == False:
            game_over = state[-1]
            possible_actions = game.possible_actions()
            #print(possible_actions)
            state = game.step(possible_actions[random.randint(0, len(possible_actions)-1)]) #pick last possible action
        points = state[-2]
        scores.append(points)
    
    print(sum(scores)/ len(scores))
            
    