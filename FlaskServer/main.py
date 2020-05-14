from flask import Flask, request
from boards import ALL_BOARDS, attribute
from game import Game, Dice, Player
import sys

app = Flask(__name__)

games = [None]

@app.route('/', methods=['GET', 'POST'])
def index():
    #starting new game:
    # send ?name=AAAA&board_name=Zywy+ogien&main_mission_color=RED
    # response with gameid

    #continue started game:
    # send ?game_id=0&dices=R4+B5+Y3+G4 if 4 dices on table
    # send &game_id=0&dices=R4+B5+Y3    if 3 dices on table
    # response with dice and position: R4+15 or 0 - no move


    name = request.args.get("name")
    board_name = request.args.get("board_name")
    main_mission_color = attribute["RED"] #STUB
    
    game_id = request.args.get("game_id")
    dices = request.args.get("dices")

    if name and board_name and main_mission_color:
        game_id = 0 #len(games)
        games[0] = Game(Player(name, ALL_BOARDS[board_name], main_mission_color)) #for now
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
        #game.dices_on_table
        return str(game.dices_on_table[0]) + "+" + "7"
    else:
        return """ <br /><br /><br />
            Unable to parse arguments!<br />
            #starting new game: <br />
            # send ?name=AAAA&board_name=Zywy+ogien&main_mission_color=RED <br />
            # response with gameid <br />
            <br />
            #continue started game:<br />
            # send ?game_id=0&dices=R4+B5+Y3+G4 if 4 dices on table<br />
            # send &game_id=0&dices=R4+B5+Y3    if 3 dices on table<br />
            # response with dice and position: R4+15 or 0 - no move<br />
            <br />
        """
    
        
    
