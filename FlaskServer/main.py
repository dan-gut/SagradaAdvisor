from flask import Flask, request
from boards import ALL_BOARDS, attribute
from game import Game, Dice, Player, Board
import greedy as advisor
import math
import sys

app = Flask(__name__)

games = []


def get_action_representation(board, action_number):
    dice_number = math.floor((action_number - 1) / board.NUMBER_OF_FIELDS)
    field_index = (action_number) % board.NUMBER_OF_FIELDS

    return dice_number, field_index


@app.route('/', methods=['GET', 'POST'])
def index():
    # starting new game:
    # send ?name=AAAA&board_name=zywy_ogien&main_mission_color=RED
    # response with gameid

    # continue started game:
    # send ?game_id=0&dices=R4+B5+Y3+G4
    # response with with two moves (dice and position) separated by '-': R4+15-B5+5 (or 0 - no move)

    name = request.args.get("name")
    board_name = request.args.get("board_name")
    main_mission_color = request.args.get("main_mission_color")
    
    game_id = request.args.get("game_id")
    dices = request.args.get("dices")

    if name and board_name and main_mission_color:
        game_id = len(games)

        try:
            games.append(Game(Player(name,
                                     Board(ALL_BOARDS[board_name], board_name),
                                     attribute[main_mission_color])))
        except KeyError:
            return "Incorrect board name!"

        return "{}".format(game_id)

    elif game_id and dices:
        game_id = int(game_id)
        dices_str = dices.split(" ")
        print(dices_str, file=sys.stderr)
        game = games[game_id]
        game.dices_on_table = []
        for dice_str in dices_str:
            temp_dice = Dice(0, 0)
            if temp_dice.initialize_with_string(dice_str) != 0:
                game.dices_on_table.append(temp_dice)
        print(game.dices_on_table, file=sys.stderr)
        print(str(game.player.board), file=sys.stderr)


        action1 = advisor.pick_best_action(game)
        game.step(action1)

        action2 = advisor.pick_best_action(game)
        game.step(action2)
                
        print(game.dices_on_table, file=sys.stderr)
        print(str(game.player.board), file=sys.stderr)
        
        ret = ""

        dice_no1 = len(dices_str)  # must be defined in case action1==0 and action2!=0
        if action1 == 0:
            ret += "0+0"
        else:
            dice_no1, field_no1 = get_action_representation(game.player.board, action1)
            ret += dices_str[dice_no1] + "+" + str(field_no1)

        ret += "-"

        

        if action2 == 0:
            ret += "0+0"
        else:
            dice_no2, field_no2 = get_action_representation(game.player.board, action2)
            if dice_no2 >= dice_no1:
                dice_no2 += 1
            ret += dices_str[dice_no2] + "+" + str(field_no2)



        return ret

    else:
        return """<br /><br /><br />
            Unable to parse arguments! <br />
            starting new game: <br />
             send ?name=AAAA&board_name=zywy_ogien&main_mission_color=RED <br />
             response with gameid <br />
            <br />
            continue started game: <br />
             send ?game_id=0&dices=R4+B5+Y3+G4 <br />
             response with with two moves (dice and position) separated by '-': R4+15-B5+5 (or 0+0 - no move) <br />
            <br />"""
