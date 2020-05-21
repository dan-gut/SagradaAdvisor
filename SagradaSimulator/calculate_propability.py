from game import Game, attribute, Player, Board

def calculate_field_propability(x, y, game):
    # print("x, y: ", x, y)
    current = game.player.board.board_view[y][x]
    left_dices = []
    left_dices.append(sum([1 for x in game._dices_to_draw_from if x.color == attribute["RED"]]))
    left_dices.append(sum([1 for x in game._dices_to_draw_from if x.color == attribute["PURPLE"]]))
    left_dices.append(sum([1 for x in game._dices_to_draw_from if x.color == attribute["YELLOW"]]))
    left_dices.append(sum([1 for x in game._dices_to_draw_from if x.color == attribute["GREEN"]]))
    left_dices.append(sum([1 for x in game._dices_to_draw_from if x.color == attribute["BLUE"]]))
    
    dices_to_pick_left = (game.NUMBER_OF_ROUNDS * game._dices_to_draw_each_round) - (game.round * game._dices_to_draw_each_round)
    left_dices_sum = sum(left_dices)

    chance_to_get_color = [1 for i in range(5)]
    for i in range(dices_to_pick_left):
        chance_to_get_color[0] *= 1 - (left_dices[0] / (left_dices_sum - i))
        chance_to_get_color[1] *= 1 - (left_dices[1] / (left_dices_sum - i))
        chance_to_get_color[2] *= 1 - (left_dices[2] / (left_dices_sum - i))
        chance_to_get_color[3] *= 1 - (left_dices[3] / (left_dices_sum - i))
        chance_to_get_color[4] *= 1 - (left_dices[4] / (left_dices_sum - i))
    
    chance_to_get_color = [1 - p for p in chance_to_get_color]

    own_prop = 1
    if current == 0:
        own_prop = 1
    elif current >= 1 and current <= 6:
        own_prop = 1 - (5/6) ** dices_to_pick_left
    elif current > 6:
        own_prop = chance_to_get_color[current - 7]

    # print(own_prop)
    properties = []
    left_prop = 1
    if x > 0:
        if game.player.board.dices[y][x - 1] == attribute["EMPTY"]:
            properties.append(game.player.board.board_view[y][x - 1])
        else:
            properties.append(game.player.board.dices[y][x - 1].color)
            properties.append(game.player.board.dices[y][x - 1].value)
    
    if x < game.player.board.BOARD_X_MAX:
        if game.player.board.dices[y][x + 1] == attribute["EMPTY"]:
            properties.append(game.player.board.board_view[y][x + 1])
        else:
            properties.append(game.player.board.dices[y][x + 1].color)
            properties.append(game.player.board.dices[y][x + 1].value)

    if y > 0:
        if game.player.board.dices[y - 1][x] == attribute["EMPTY"]:
            properties.append(game.player.board.board_view[y - 1][x])
        else:
            properties.append(game.player.board.dices[y - 1][x].color)
            properties.append(game.player.board.dices[y - 1][x].value)
    
    if y < game.player.board.BOARD_Y_MAX:
        if game.player.board.dices[y + 1][x] == attribute["EMPTY"]:
            properties.append(game.player.board.board_view[y + 1][x])
        else:
            properties.append(game.player.board.dices[y + 1][x].color)
            properties.append(game.player.board.dices[y + 1][x].value)

    
    # properties = list(set(properties))
    properties = [prop for prop in properties if prop != 0]
    # print(properties)
    other_prob = 1
    for prop in properties:
        if prop <= attribute["SIX"]:
            other_prob *= 1 - (5/6) ** dices_to_pick_left
        elif prop <= attribute["GREEN"]:
            other_prob *= chance_to_get_color[prop - 7]
        else:
            print("error")
        # print(other_prob)
    
    # print(x, y, own_prop, other_prob, own_prop * other_prob, properties, dices_to_pick_left)
    return own_prop * other_prob

#    if x == 0:

if __name__ == "__main__":
    board = Board([
        [attribute["THREE"], attribute["FOUR"], attribute["ONE"],    attribute["FIVE"],   attribute["ALL"]],
        [attribute["ALL"],   attribute["SIX"],  attribute["TWO"],    attribute["ALL"],    attribute["YELLOW"]],
        [attribute["ALL"],   attribute["ALL"],  attribute["ALL"],    attribute["YELLOW"], attribute["RED"]],
        [attribute["FIVE"],  attribute["ALL"],  attribute["YELLOW"], attribute["RED"],    attribute["SIX"]]

    ], "Zywy ogien")

    game = Game(Player("Pawel", board, attribute["RED"]))
    game.reset()
    for y in range(Board.BOARD_Y_MAX + 1):
        for x in range(Board.BOARD_X_MAX + 1):
            print(round(calculate_field_propability(x, y, game), 6), end = " ")
        print()
    
    
    print("dices on table:")
    [print(str(d), end=" ") for d in game.dices_on_table]
    print()
    game.step(23)
    for y in range(Board.BOARD_Y_MAX + 1):
        for x in range(Board.BOARD_X_MAX + 1):
            print(round(calculate_field_propability(x, y, game), 6), end = " ")
        print()