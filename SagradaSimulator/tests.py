import unittest
from game import *

class TestSagradaGame(unittest.TestCase):

    def setUp(self):
        self.board = Board([
            [Attribute.THREE, Attribute.FOUR, Attribute.ONE,    Attribute.FIVE,   Attribute.ALL],
            [Attribute.ALL,   Attribute.SIX,  Attribute.TWO,    Attribute.ALL,    Attribute.YELLOW],
            [Attribute.ALL,   Attribute.ALL,  Attribute.ALL,    Attribute.YELLOW, Attribute.RED],
            [Attribute.FIVE,  Attribute.ALL,  Attribute.YELLOW, Attribute.RED,    Attribute.SIX]

        ], "Zywy ogien")

    def test_can_put_dice(self):
        dice = Dice(Attribute.RED, Attribute.SIX)
        self.assertEqual(self.board._can_put_dice(0,0, dice), False)
        self.assertEqual(self.board._can_put_dice(1,1, dice), False)
        dice = Dice(Attribute.RED, Attribute.THREE)
        self.assertEqual(self.board._can_put_dice(0,0, dice), True)
        dice = Dice(Attribute.RED, Attribute.THREE)
        self.assertEqual(self.board._can_put_dice(1,3, dice), True)
        self.assertEqual(self.board._can_put_dice(0,3, dice), False)
        self.assertEqual(self.board._can_put_dice(3,3, dice), True)

    def test_get_possible_actions(self):
        dices = [
            Dice(Attribute.RED, Attribute.SIX), 
            Dice(Attribute.RED, Attribute.THREE), 
            Dice(Attribute.RED, Attribute.ONE), 
            Dice(Attribute.BLUE, Attribute.THREE)
            ]

        possible_actions = self.board.get_possible_actions(dices)
        self.assertEqual(possible_actions[0],  None)
        self.assertEqual(possible_actions[1],  [0, 1, dices[0]])
        self.assertEqual(possible_actions[2],  [0, 2, dices[0]])
        self.assertEqual(possible_actions[3],  [0, 0, dices[1]])
        self.assertEqual(possible_actions[4],  [0, 1, dices[1]])
        self.assertEqual(possible_actions[5],  [0, 2, dices[1]])
        self.assertEqual(possible_actions[6],  [0, 1, dices[2]])
        self.assertEqual(possible_actions[7],  [0, 2, dices[2]])
        self.assertEqual(possible_actions[8],  [2, 0, dices[2]])
        self.assertEqual(possible_actions[9],  [0, 0, dices[3]])
        self.assertEqual(possible_actions[10], [0, 1, dices[3]])
        self.assertEqual(possible_actions[11], [0, 2, dices[3]])

if __name__ == "__main__":
    unittest.main()