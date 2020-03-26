from enum import Enum

class Attribute(Enum):
    '''
    We have 13 possible states on board
    0: everything can be placed there (grey)
    1 - 6: like number on dice
    colors: RED, PURPLE, YELLOW, RED, BLUE, GREEN
    '''
    ALL = 0

    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6

    RED = 7
    PURPLE = 8
    YELLOW= 9
    BLUE = 10
    GREEN = 11

class Dice:
    def __init__(self, color, value):
        self.color = color #7 - 11
        self.value = value #1 - 6
        

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
        self.dices = [
                      [None, None, None, None, None],
                      [None, None, None, None, None],
                      [None, None, None, None, None],
                      [None, None, None, None, None]
                     ]
        self._no_dices = True

    def calculate_points(self):
        pass

    def put_dice(self, x, y, dice):
        '''Should not allow to put dice in incorrect position'''
        pass

    def put_dice_force(self, x, y, dice):
        '''Should allow to put dice in incorrect position'''
        pass

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
        if self.dices[y][x] != None:
            return False
        
        if dice.color != self.board_view[y][x] and dice.value != self.board_view[y][x] and self.board_view[y][x] != Attribute.ALL:
            return False

        #3.
        if y > Board.BOARD_Y_MIN and self.dices[y - 1][x] != None:
            if self.dices[y - 1][x].color == dice.color or self.dices[y - 1][x].value == dice.value: return False

        if y < Board.BOARD_Y_MAX and self.dices[y + 1][x] != None:
            if self.dices[y + 1][x].color == dice.color or self.dices[y + 1][x].value == dice.value: return False
        
        if x > Board.BOARD_X_MIN and self.dices[y][x - 1] != None:
            if self.dices[y][x - 1].color == dice.color or self.dices[y][x - 1].value == dice.value: return False

        if x < Board.BOARD_X_MAX and self.dices[y][x + 1] != None:
            if self.dices[y][x + 1].color == dice.color or self.dices[y][x + 1].value == dice.value: return False

        #4b.
        if self._no_dices:
            if ((x == Board.BOARD_X_MIN or x == Board.BOARD_X_MAX) or
                (y == Board.BOARD_Y_MIN or y == Board.BOARD_Y_MAX)):
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

                if self.dices[y + y_delta][x + x_delta] is not None:
                    return True
        

        return True


class Player:
    def __init__(self):
        pass

if __name__ == "__main__":
    board = Board([
        [Attribute.THREE, Attribute.FOUR, Attribute.ONE, Attribute.FIVE, Attribute.ALL],
        [Attribute.ALL, Attribute.SIX, Attribute.TWO, Attribute.ALL, Attribute.YELLOW],
        [Attribute.ALL, Attribute.ALL, Attribute.ALL, Attribute.YELLOW, Attribute.RED],
        [Attribute.FIVE, Attribute.ALL, Attribute.YELLOW, Attribute.RED, Attribute.SIX]

    ], "Zywy ogien")

    #some tests
    dice = Dice(Attribute.RED, Attribute.SIX)
    assert(board._can_put_dice(0,0, dice) == False)
    assert(board._can_put_dice(1,1, dice) == False)
    dice = Dice(Attribute.RED, Attribute.THREE)
    assert(board._can_put_dice(0,0, dice) == True)
    dice = Dice(Attribute.RED, Attribute.THREE)
    assert(board._can_put_dice(1,3, dice) == True)
    assert(board._can_put_dice(0,3, dice) == False)
    assert(board._can_put_dice(3,3, dice) == True)
