from mcts import MCTS
import game as simulator

atr = simulator.attribute

board = simulator.Board([
    [atr["THREE"], atr["FOUR"], atr["ONE"], atr["FIVE"], atr["ALL"]],
    [atr["ALL"], atr["SIX"], atr["TWO"], atr["ALL"], atr["YELLOW"]],
    [atr["ALL"], atr["ALL"], atr["ALL"], atr["YELLOW"], atr["RED"]],
    [atr["FIVE"], atr["ALL"], atr["YELLOW"], atr["RED"], atr["SIX"]]

], "Zywy ogien")

game = simulator.Game(simulator.Player("Daniel", board, atr["RED"]))

mcts = MCTS(c_val=2)

mcts.load_data("mcts_data.dat")


s, r, game_finished = game.reset()
while not game_finished:
    action, not_random = mcts.best_choice(game) 
    for dice in game.dices_on_table:
        print(str(dice), end=" ")
    print()
    print(str(game.player.board))
    print(action, not_random)
    s, r, game_finished = game.step(action)
    print("reward:", r)
    # log.info(f"isNotRandom: {not_random}")
    