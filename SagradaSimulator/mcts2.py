from mcts import mcts
import game as simulator
import copy

class State():
    def __init__(self):
        self.s = None
        self.r = 0
        self.done = False

        atr = simulator.attribute

        board = simulator.Board([
        [atr["THREE"], atr["FOUR"], atr["ONE"], atr["FIVE"], atr["ALL"]],
        [atr["ALL"], atr["SIX"], atr["TWO"], atr["ALL"], atr["YELLOW"]],
        [atr["ALL"], atr["ALL"], atr["ALL"], atr["YELLOW"], atr["RED"]],
        [atr["FIVE"], atr["ALL"], atr["YELLOW"], atr["RED"], atr["SIX"]]

        ], "Zywy ogien")

        self.game = simulator.Game(simulator.Player("Pablo", board, atr["RED"]))
        self.game.reset()

    def getPossibleActions(self):
        state = self.game.get_current_state()
        
        temp = [Action(state, action) for action in self.game.possible_actions()]
        if len(temp) > 1:
            return temp[1:]
        # [print(a.action, end=" ") for a in temp]
        # print()
        return temp

    def takeAction(self, action):
        # print("action", action.action)
        newState = copy.deepcopy(self)
        newState.s, newState.r, newState.done = newState.game.step(action.action)
        # self.new_s, self.r, self.done = self.game.step(action.action)
        return newState

    def isTerminal(self):
        return self.done

    def getReward(self):
        # print(self.game.player.calculate_points())
        return self.game.player.calculate_points()

class Action:
    def __init__(self, game_state, action):
        self.g_state = game_state
        self.action = action

    def __hash__(self):
        return hash((self.g_state, self.action))

if __name__ == "__main__":
    # print(str(state.game.player.board))
    state = State()
    print(str(state.game.player.board))
    mcts = mcts(timeLimit=500)
    for i in range(18):
        action = mcts.search(initialState = state)
        # print(action.g_state, action.action)
        state = state.takeAction(action)
    
    print(str(state.game.player.board))
    