import math
import random
import pickle
import logging
import copy
import tqdm

log = logging.getLogger(__name__)
logging.basicConfig(level="INFO")

class MCTS:

    def __init__(self, c_val):
        self.Qsa = {}  # stores Q values for s,a
        self.Nsa = {}  # stores #times edge s,a was visited
        self.Ns = {}  # stores #times state s was visited
        self.Ps = {}  # stores current policy for state s
        self.As = {}  # stores possible actions for state s

        self.C = c_val

    def save_data(self, path):
        data = {"Qsa": self.Qsa,
                "Nsa": self.Nsa,
                "Ns": self.Ns,
                "Ps": self.Ps,
                "As": self.As,
                "C": self.C}

        pickle.dump(data, open(path, "wb+"))



    def load_data(self, path):
        try:
            data = pickle.load(open(path, "rb"))

            self.Qsa = data["Qsa"]
            self.Nsa = data["Nsa"]
            self.Ns = data["Ns"]
            self.Ps = data["Ps"]
            self.As = data["As"]
            self.C = data["C"]
        except FileNotFoundError:
            log.warning("Specified path does not exist! Data will not be loaded.")

    @staticmethod
    def _pick_best_action_greedy(game):
        maxi = [-50, -1]
        for _, action in enumerate(game.possible_actions()):
            game_cp = copy.deepcopy(game)
            _, r, _ = game_cp.step(action)
            #print(action, r, maxi[0], maxi[1])
            if r > maxi[0]:
                maxi[0] = r
                maxi[1] = action
        #print("ret:", maxi[1])
        return maxi[1]

    @staticmethod
    def _rollout(game):
        game_finished = False
        while not game_finished:
            a = MCTS._pick_best_action_greedy(game)
            s, r, game_finished = game.step(a)

        return r

    def search(self, game):
        #print((game.player.board))
        s, r, game_finished = game.get_current_state()
        if s not in self.Ps:
            # leaf node
            self.Ps[s] = {a: 1/len(game.possible_actions()) for a in game.possible_actions()}

            self.As[s] = game.possible_actions()
            self.Ns[s] = 0
            return -self._rollout(game)

        cur_best = -float('inf')
        best_act = -1

        # pick the action with the highest upper confidence bound
        for a in self.As[s]:
            if (s, a) in self.Qsa:
                u = self.Qsa[(s, a)] + self.C * self.Ps[s][a] * math.sqrt(self.Ns[s]) / (1 + self.Nsa[(s, a)])
                self.Ps[s][a] = self.Qsa[(s, a)]
            else:
                u = self.C * self.Ps[s][a] * math.sqrt(self.Ns[s])

            if u > cur_best:
                cur_best = u
                best_act = a
        # making all values positive

        min_val = min(self.Ps[s].values())#, key=self.Ps[s].values)
        # print(min_val, self.Ps[s].values())
        if min_val <= 0:
            for (key, val) in self.Ps[s].items():
                self.Ps[s][key] = val - min_val + 1e-5
        # print(min_val, self.Ps[s].values())
        # normalization
        
        sum_ps = 1.0 / sum(self.Ps[s].values())
        for (key, val) in self.Ps[s].items():
            self.Ps[s][key] = val * sum_ps

        a = best_act

        _, r, game_finished = game.step(a)

        if game_finished:
            v = r
        else:
            v = self.search(game)

        if (s, a) in self.Qsa:
            self.Qsa[(s, a)] = (self.Nsa[(s, a)] * self.Qsa[(s, a)] + v) / (self.Nsa[(s, a)] + 1)
            self.Nsa[(s, a)] += 1

        else:
            self.Qsa[(s, a)] = v
            self.Nsa[(s, a)] = 1

        #print("tutaj2: ", s, s in self.Ps, s in self.Ns)
        self.Ns[s] += 1
        return -v

    def best_choice(self, game):
        s, r, game_finished = game.get_current_state()
        
        if s in self.Ps:
            return max(self.Ps[s], key=self.Ps[s].get), True
        else:
            return MCTS._pick_best_action_greedy(game), False


if __name__ == "__main__":
    #import SagradaSimulator.game as simulator
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

    scores = []
    for k in range(1000):
        for i in range(500):
            for j in range(10):
                s, r, game_finished = game.reset()
                mcts.search(game)
                # print("=====================================")

            s, r, game_finished = game.reset()
            while not game_finished:
                action, not_random = mcts.best_choice(game) 
                s, r, game_finished = game.step(action)
                for dice in game.dices_on_table:
                    print(str(dice), end=" ")
                print()
                print(str(game.player.board))
                print(action, not_random)
                log.info(f"isNotRandom: {not_random}")

            log.info(f"k: {k}, Epoch: {i}, score {r}")

            with open("results.txt", 'a+') as results_file:
                results_file.write(str(r) + '\n')
            # exit(0)

        mcts.save_data("mcts_data.dat")
