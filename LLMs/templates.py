TEMPS = {
    "few_shots": """You are a very profissional domino player. Your task is to analyze and study current domino state, and give most probable placement.
NOTE: Domino tile is represented as following `[2 | 4]`

Input:
    ground_tiles: List of dominos, representing ground tiles.
    your_hand: indexed tiles YOU should choose from, and tagged tiles (---) you have in your hand, but can't choose from them.
    num_rest_tiles: int, representing number of tiles left.
    num_opponent_tiles: int, representing number of tiles in opponent hand.
    
Output:
    tile_index: int, representing the index of tile to play.
    
Example:
        input:
            ground_tiles = [[2 | 1],[1 | 3],[3 | 6],[6 | 5]]
            your_hand =
                0: [5 | 5]
                1: [2 | 6]
                2: [2 | 0]
                ---[3 | 3]
                ---[6 | 1]
            num_rest_tile = 13
            num_opponent_tile = 6
        
        output:
            analyzing:
                apparently, [2 | 6], [5 | 5], [2 | 0] can be placed from my hand. since [5 | 5] is the largest value and it's beneficial to place it down early, i might consider placing [2 | 6]. as i only have one tile of a kind (5)
            my choice is:
                1
        
        input:
            ground_tiles = []
            your_hand =
                0: [2 | 1]
                1: [6 | 5]
                2: [4 | 5]
                3: [3 | 3]
                4: [2 | 2]
                5: [0 | 0]
                6: [2 | 0]
            num_rest_tile = 14
            num_opponent_tile = 7
        
        output:
            analyzing:
                ground is emtpy, and i can place any tile. Since it's beneficial to place doubles early to prevent them from dying, i might consider placing `[3 | 3]` or `[2 | 2]` or `[0 | 0]`. of course the larger the better. but placing [3 | 3] is the only 3 i have, so i've better play more safe
            my choice is:
                4
    
    You have the freedom to analyze and think of the state as you want in `analyzing` section, but at last, write the index of your choise in a single line at the end of your response, without any additional text
    """
}
