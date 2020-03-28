import unittest
from game import *
import copy

class TestSagradaGame(unittest.TestCase):

    def setUp(self):
        self.board = Board([
            [attribute["THREE"], attribute["FOUR"], attribute["ONE"],    attribute["FIVE"],   attribute["ALL"]],
            [attribute["ALL"],   attribute["SIX"],  attribute["TWO"],    attribute["ALL"],    attribute["YELLOW"]],
            [attribute["ALL"],   attribute["ALL"],  attribute["ALL"],    attribute["YELLOW"], attribute["RED"]],
            [attribute["FIVE"],  attribute["ALL"],  attribute["YELLOW"], attribute["RED"],    attribute["SIX"]]
        ], "Zywy ogien")

    def test_can_put_dice(self):
        dice = Dice(attribute["RED"], attribute["SIX"])
        self.assertEqual(self.board._can_put_dice(0,0, dice), False)
        self.assertEqual(self.board._can_put_dice(1,1, dice), False)
        dice = Dice(attribute["RED"], attribute["THREE"])
        self.assertEqual(self.board._can_put_dice(0,0, dice), True)
        dice = Dice(attribute["RED"], attribute["THREE"])
        self.assertEqual(self.board._can_put_dice(1,3, dice), True)
        self.assertEqual(self.board._can_put_dice(0,3, dice), False)
        self.assertEqual(self.board._can_put_dice(3,3, dice), True)

    def test_get_field_binary_representation(self):
        self.assertEqual(self.board._get_field_binary_representation(0, 0), int('0b0000000011', 2))
        self.assertEqual(self.board._get_field_binary_representation(0, 2), 0)
        
        self.board.put_dice(0, 0, Dice(attribute["RED"], attribute['THREE']))
        self.assertEqual(self.board._get_field_binary_representation(0, 0), int('0b0110010011', 2))

        self.board.put_dice(4, 3, Dice(attribute['GREEN'], attribute['SIX']))
        self.assertEqual(self.board._get_field_binary_representation(4, 3), int('0b1101010110', 2))
    
    def test_get_field_one_hot_representation(self):
        zeros = [0 for i in range(27)]
        
        zeros_copy = copy.deepcopy(zeros)
        zeros_copy[14 + 3] = 1 #THREE
        zeros_copy[0] = 1      #no value
        zeros_copy[7] = 1      #no color
        self.assertEqual(self.board._get_field_one_hot_representation(0, 0), zeros_copy)

        zeros_copy = copy.deepcopy(zeros)
        zeros_copy[14 + 0] = 1 #all
        zeros_copy[0] = 1      #no value
        zeros_copy[7] = 1      #no color
        self.assertEqual(self.board._get_field_one_hot_representation(0, 2), zeros_copy)
        
        self.board.put_dice(0, 0, Dice(attribute["RED"], attribute['THREE']))
        zeros_copy = copy.deepcopy(zeros)
        zeros_copy[14 + 3] = 1 #THREE
        zeros_copy[3] = 1      #THREE
        zeros_copy[8] = 1      #RED
        self.assertEqual(self.board._get_field_one_hot_representation(0, 0), zeros_copy)

        self.board.put_dice(4, 3, Dice(attribute['GREEN'], attribute['SIX']))
        zeros_copy = copy.deepcopy(zeros)
        zeros_copy[14 + 6] = 1 #SIX
        zeros_copy[6] = 1      #SIX
        zeros_copy[7 + 5] = 1  #GREEN
        self.assertEqual(self.board._get_field_one_hot_representation(4, 3), zeros_copy)

    def test_get_dices_on_table_one_hot(self):
        player = Player("test", self.board, attribute["RED"])
        game = Game(player)
        game.dices_on_table = [ \
            Dice(attribute['RED'], attribute['ONE']), \
            Dice(attribute['GREEN'], attribute['TWO']), \
            Dice(attribute['BLUE'], attribute['THREE']), \
            #empty_dice
            ]
        
        one_hot = game.get_dices_on_table_one_hot()
        self.assertEqual(one_hot, [\
            0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0,
            0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1,
            0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0,
            1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
            ])


if __name__ == "__main__":
    unittest.main()