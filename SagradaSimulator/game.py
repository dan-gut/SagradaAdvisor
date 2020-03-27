from enum import Enum
import random

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

    "RED"    :   7,
    "PURPLE" :   8,
    "YELLOW" :   9,
    "BLUE"   :  10,
    "GREEN"  :  11,

    "EMPTY"  :  12,
}

class Dice:
    def __init__(self, color, value):
        self.color = color #7 - 11
        self.value = value #1 - 6
    
    @staticmethod
    def get_random_dice(color):
        return Dice(color, random.randint(1, 6))

    def __str__(self):
        return "Dice: " + "C: " + str(self.color) +  " V: " +  str(self.value)
        

class Board:
    BOARD_X_MIN = 0
    BOARD_X_MAX = 4
    BOARD_Y_MIN = 0
    BOARD_Y_MAX = 3
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
        

        return True

    def get_possible_actions(self, dices):
        actions = [None] #it is always possible to do nothing
        for dice in dices:
            for x in range(Board.BOARD_X_MAX + 1):
                for y in range(Board.BOARD_Y_MAX + 1):
                    if self._can_put_dice(x, y, dice):
                        actions.append([x, y, dice])
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
        for i in range(count):
            random_index = random.randint(0, len(self._dices_to_draw_from) - 1)
            self.dices_on_table.append(self._dices_to_draw_from.pop(random_index))

    def _action_out(self):
        '''
        function will return:
             - dices on table (that were randomly picked), 
             - number of dices to pick left 
             - current player's board_view (what can be put where) 
             - dices (where are dices on board), as list of digits - see Enum Attributes
             - player points
             - bool if game is finished (True == finished)
        '''

        return (self.dices_on_table, 
                Game.DICES_TO_PICK_BY_PLAYER - self.player.move_counter, 
                self.player.board.board_view,
                self.player.board.dices,
                self.player.calculate_points(),
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
        self.toss_random_dices(self._dices_to_draw_each_round)

    def step(self, action):
        '''For one player, he has to pick 2 dices out of four, one step will be to pick dice and put it in correct position
            function return value: see self._action_out(self) function
            action parameter has to be in format:
                [x, y, dice]
            or None if no action is performed (skip move)
        ''' 
        if self._game_finished:
            return self._action_out()
        
        self.round += 1

        self.player.move_counter += 1
        if action == None:
            pass
        else:
            if self.player.board.put_dice(*action):
                self.dices_on_table.remove(action[2])
            else:
                raise RuntimeError("Cannot put dice there!")
        
        if self.round == Game.NUMBER_OF_ROUNDS:
            self._game_finished = True
            return self._action_out()


        if self.player.move_counter == 2:
            self.next_round()
        
        return self._action_out()

if __name__ == "__main__":
    board = Board([
        [attribute["THREE"], attribute["FOUR"], attribute["ONE"],    attribute["FIVE"],   attribute["ALL"]],
        [attribute["ALL"],   attribute["SIX"],  attribute["TWO"],    attribute["ALL"],    attribute["YELLOW"]],
        [attribute["ALL"],   attribute["ALL"],  attribute["ALL"],    attribute["YELLOW"], attribute["RED"]],
        [attribute["FIVE"],  attribute["ALL"],  attribute["YELLOW"], attribute["RED"],    attribute["SIX"]]

    ], "Zywy ogien")

    game = Game(Player("Pawel", board, attribute["RED"]))
    state = game.reset()
    game_over = state[-1]
    while game_over == False:
        points = state[-2]
        game_over = state[-1]
        possible_actions = game.possible_actions()
        print(points)
        
        state = game.step(possible_actions[-1]) #pick last possible action
        
    