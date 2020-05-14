'''
#     We have 13 possible states on board
#     0: everything can be placed there (grey)
#     1 - 6: like numbers on dice
#     colors: RED, PURPLE, YELLOW, RED, BLUE, GREEN
#     empty: 12
#     '''

attribute = {
    "ALL"    :   0,
    "ONE"    :   1,
    "TWO"    :   2,
    "THREE"  :   3,
    "FOUR"   :   4,
    "FIVE"   :   5,
    "SIX"    :   6,

    "RED"    :   7, #1
    "PURPLE" :   8, #2
    "YELLOW" :   9, #3
    "BLUE"   :  10, #4
    "GREEN"  :  11, #5

    "EMPTY"  :  12,
}

num_to_color = {0: "A", 1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7 : "R", 8: "P", 9:"Y", 10:"B", 11:"G"}


ALL_BOARDS = { 
    "zywy_ogien": 
    [
        [attribute["THREE"], attribute["FOUR"], attribute["ONE"],    attribute["FIVE"],   attribute["ALL"]],
        [attribute["ALL"],   attribute["SIX"],  attribute["TWO"],    attribute["ALL"],    attribute["YELLOW"]],
        [attribute["ALL"],   attribute["ALL"],  attribute["ALL"],    attribute["YELLOW"], attribute["RED"]],
        [attribute["FIVE"],  attribute["ALL"],  attribute["YELLOW"], attribute["RED"],    attribute["SIX"]]
    ],
    
    "gwiezdny_pyl":
    [
        [attribute["ALL"],   attribute["ONE"],   attribute["GREEN"], attribute["PURPLE"], attribute["FOUR"]],
        [attribute["SIX"],   attribute["PURPLE"],attribute["TWO"],   attribute["FIVE"],   attribute["GREEN"]],
        [attribute["ONE"],   attribute["GREEN"], attribute["FIVE"],  attribute["THREE"],  attribute["PURPLE"]],
        [attribute["ALL"],   attribute["ALL"],   attribute["ALL"],   attribute["ALL"],    attribute["ALL"]]
    ],

    "woda_i_ogien":
    [
        [attribute["ALL"],   attribute["BLUE"],  attribute["RED"],   attribute["ALL"],    attribute["ALL"]],
        [attribute["ALL"],   attribute["FOUR"],  attribute["FIVE"],  attribute["ALL"],    attribute["BLUE"]],
        [attribute["BLUE"],  attribute["TWO"],   attribute["ALL"],   attribute["RED"],    attribute["FIVE"]],
        [attribute["SIX"],   attribute["RED"],   attribute["THREE"], attribute["ONE"],    attribute["ALL"]]
    ],
    
    "dwa_swiaty": 
    [
        [attribute["ALL"],   attribute["ALL"],   attribute["ALL"],   attribute["RED"],    attribute["FIVE"]],
        [attribute["ALL"],   attribute["ALL"],   attribute["PURPLE"],attribute["FOUR"],   attribute["BLUE"]],
        [attribute["ALL"],   attribute["BLUE"],  attribute["THREE"], attribute["YELLOW"], attribute["SIX"]],
        [attribute["YELLOW"],attribute["TWO"],   attribute["GREEN"], attribute["ONE"],    attribute["FOUR"]]
    ]
    
    # "ALL": 
    # [
    #     [attribute["ALL"],   attribute["ALL"],   attribute["ALL"],   attribute["ALL"],    attribute["ALL"]],
    #     [attribute["ALL"],   attribute["ALL"],   attribute["ALL"],   attribute["ALL"],    attribute["ALL"]],
    #     [attribute["ALL"],   attribute["ALL"],   attribute["ALL"],   attribute["ALL"],    attribute["ALL"]],
    #     [attribute["ALL"],   attribute["ALL"],   attribute["ALL"],   attribute["ALL"],    attribute["ALL"]]
    # ],
}
