from game import *
import logging
import copy


def pick_best_action(game):
    maxi = [-1, 0]
    possible_actions = game.possible_actions()
    print(possible_actions)
    for i in range(len(possible_actions)):
        game_cp = copy.deepcopy(game)
        _, r, _, _ = game_cp.step(possible_actions[i])
        if r > maxi[0]:
            maxi[0] = r
            maxi[1] = possible_actions[i]
        
    return maxi[1]


if __name__ == "__main__":
    from FlaskServer.boards import ALL_BOARDS, attribute
    logging.getLogger().setLevel(logging.INFO)

    game = Game(Player("Daniel", Board(ALL_BOARDS["zywy_ogien"], "zywy_ogien"), main_mission_color=attribute["RED"]))

    dices_str = "R4 B5 Y3 G4".split(" ")
    game.dices_on_table = []
    for dice_str in dices_str:
        temp_dice = Dice(0, 0)
        if temp_dice.initialize_with_string(dice_str) != 0:
            game.dices_on_table.append(temp_dice)

    action = pick_best_action(game)
    logging.info(f"Chosen action: {action}")
    state = game.step(action)
    logging.info(f"Result: {state[1]}")

    action = pick_best_action(game)
    logging.info(f"Chosen action: {action}")
    state = game.step(action)
    logging.info(f"Result: {state[1]}")

