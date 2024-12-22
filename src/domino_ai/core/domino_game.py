import os
import platform
import random
from typing import List, Literal, Union
import copy
import logging


from .domino_components import (
    generate_domino_set,
    Domino,
    Player,
    AI_Player,
    check_play,
    orient_if_needed,
)
from .utils import validate_direction, validate_idx
from .cli_interactions import cli_feedback


def clear_terminal():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")


# make use of logging if you make 2 AI compete each other
logging.basicConfig(filename="logging.txt", filemode="w", level=logging.INFO)


class DominoState:
    def __init__(
        self,
        ground: List[Domino],
        tiles: List[Domino],
        players: List[Player],
        turn_idx: int,
    ):
        self.ground = ground
        self.tiles = tiles
        self.players = players
        self.turn_idx = turn_idx

    def __repr__(self):
        return f"<DominoState(ground={self.ground}, tiles={self.tiles}, players={self.players}, turn_idx={self.turn_idx})>"

    def __str__(self):
        return f"DominoState:\nGround: {self.ground}\nTiles: {self.tiles}\nPlayers: {self.players}\nTurn Index: {self.turn_idx}"

    def copy(self):
        return copy.deepcopy(self)

    def change_turn(self):
        self.turn_idx = (self.turn_idx + 1) % 2


class DominoGame:
    def __init__(self, players: Literal["player", "ai"] = ["player", "ai"], seed=None):
        self.players_types = players
        self.num_players = len(players)
        self.players: List[Player] = []
        for i, p in enumerate(players):
            if "player" in p:
                self.players.append(Player(f"player {i+1}"))
            else:
                self.players.append(AI_Player(f"ai {i+1}"))

        if seed:
            random.seed(seed)

    def get_initial_state(self):
        """deals tiles after generating domino tile set.

        Returns:
            DominoState: initial domino state
        """
        tiles = generate_domino_set()
        random.shuffle(tiles)
        # deal tiles
        self.players[0].set_hand(tiles[:7])
        self.players[1].set_hand(tiles[7:14])
        ground = []
        del tiles[:14]

        turn_idx = 0
        state = DominoState(ground, tiles, self.players, turn_idx)
        return state

    def get_ground_ends(self, ground: List[Domino]):
        """returns ground tiles ends

        Args:
            ground (List[Domino]): ground tiles

        Returns:
            Tuple(int,int): left and right ground tiles ends
        """
        l, r = ground[0].left, ground[-1].right
        return l, r

    def get_valid_moves(self, player: Union[Player, AI_Player], ground: List[Domino]):
        """traverses player's hand, and check validity of each tile. And writes the result onto player object.

        Args:
            player (Player): player to check his valid placements
            ground (List[Domino]): ground tiles

        Returns:
            List[Tuple[bool,bool]]: validity of each tile in player's hand
        """
        hand = player.hand
        conditions = [check_play(ground, tile) for tile in hand]
        player.conditions = conditions

        return conditions

    def get_next_state(
        self, state: DominoState, action: Domino, player: Union[Player, AI_Player]
    ):
        """given current state, action(Domino to place) and the player performing action, this function returns the next state.

        Args:
            state (DominoState): _description_
            action (Domino): _description_
            player (Union[Player,AI_Player]): _description_

        Raises:
            e: An expection if anything goes wrong

        Returns:
            DominoState: next
        """
        try:
            condition = player.conditions[player.hand.index(action)]
        except Exception as e:
            raise e

        if all(condition):
            if type(player) is Player and (
                state.ground[-1].right != state.ground[0].left
            ):
                direction = validate_direction()
            else:
                try:
                    direction = player.double_ended_tile_score
                except:
                    direction = random.choice(["r", "l"])

            l, r = self.get_ground_ends(state.ground)
            if direction == "r":
                state.ground.append(orient_if_needed(l, r, action, direction))
            else:
                state.ground.insert(0, orient_if_needed(l, r, action, direction))
        elif condition[0]:
            state.ground.insert(0, action)
        elif condition[1]:
            state.ground.append(action)

        player.hand.remove(action)
        action.color = state.turn_idx
        return state

    def check_win(self, state: DominoState):
        """checks if a player has won the game, and returns winner id

        Args:
            state (DominoState): current game state

        Returns:
            int: winner id
        """

        idx = None
        for i, player in enumerate(state.players):
            if len(player.hand) == 0:
                idx = state.players.index(player)
                logging.info(f"  WINNER, winner:{state.players[idx].name}")
                break
        return idx

    def check_deadend(self, state: DominoState):
        """checks if a player has reached a deadend, and returns winner id

        Args:
            state (DominoState): current game state

        Returns:
            int: winner id"""

        if not state.ground:
            return False
        l, r = self.get_ground_ends(state.ground)
        if l != r:
            return False
        for player in state.players:
            for tile in player.hand:
                if l in tile:
                    return False
        for tile in state.tiles:
            if l in tile:
                return False

        winner = min(
            enumerate([player.count_hand() for player in state.players]),
            key=lambda x: x[1],
        )[0]
        logging.info(f"  DEADEND, winner:{state.players[winner].name}")
        return winner

    def update_score(state: DominoState, winner: int):
        """updates winning player's score given winner id

        Args:
            state (DominoState): current domino state
            winner (int): winner idx
        """
        res = sum(
            [
                player.count_hand()
                for i, player in enumerate(state.players)
                if i != winner
            ]
        )
        state.players[winner].score += res

    def evaluate_state(self, state: DominoState):
        """State evaluation for MCTS. It only favours less hand value. Under development to perform more sophisticated evaluation.


        Args:
            state (DominoState): current domino state

        Returns:
            int: state evaluation
            bool: state termination condition
        """
        ai = state.players[1]
        player_with_turn = state.players[state.turn_idx]
        val = -1 * (ai.count_hand())
        is_terminal = not any(
            any(condition)
            for condition in self.get_valid_moves(player_with_turn, state.ground)
        )

        return val, is_terminal

    def casual_game(self, placement_context, final_score=101, cls=True):
        """casual gameplay logic. It consists of the following steps:
        1- runs untill no player has won
        2- checks for placements avalablity for current player, if None? it's either draw or skip(if no tiles left)
        3- perform CLI interaction with user(if human)
        4- generate next state
        5- terminate round if it's over -either player has won, or it's deadend-


        Args:
            placement_context (PlacementContext): context which performs AI strategy
            final_score (int, optional): score at which game is over. Defaults to 100.

        Raises:
            e: _description_
        """
        game = self
        state = game.get_initial_state()

        while all([player.score <= final_score for player in state.players]):
            logging.info(f"\n{state}")
            logging.info(f"player turn {state.turn_idx}\n")

            if cls:
                clear_terminal()

            valid_moves = game.get_valid_moves(
                state.players[state.turn_idx], state.ground
            )

            if not any([any(placement) for placement in valid_moves]):
                if len(state.tiles) > 0:
                    # logging.info(f"Drawing tiles for {state.players[player].name}")
                    tile = state.tiles.pop()
                    while (
                        not any(check_play(state.ground, tile)) and len(state.tiles) > 0
                    ):
                        state.players[state.turn_idx].append_tile_to_hand(tile)
                        tile = state.tiles.pop()
                    state.players[state.turn_idx].append_tile_to_hand(tile)
                    continue

                else:
                    # logging.info(f"SKIPPING TURN, No valid moves for  {state.players[player].name}")
                    try:
                        state.change_turn()
                        valid_moves = game.get_valid_moves(
                            state.players[state.turn_idx], state.ground
                        )
                    except Exception as e:
                        logging.info(e)
                        logging.info(state)
                        raise e

            if state.turn_idx == 0 and type(state.players[state.turn_idx]) == Player:
                ui_tiles = cli_feedback(state)
                idx = validate_idx(len(ui_tiles))
                action = ui_tiles[idx]
            else:
                action = placement_context.calc(state)

            state = game.get_next_state(state, action, state.players[state.turn_idx])

            # checking whether win or dead-end
            c_win, c_deadend = game.check_win(state), game.check_deadend(state)
            winner = c_win if c_win is not None else c_deadend

            if type(winner) == int:
                logging.info(f"  WINNER, winner:{state}\naction:{action}")
                game.update_score(winner)
                print("round over")
                state = game.get_initial_state()
                state.turn_idx = winner
                continue
            state.change_turn()
        clear_terminal()

        print("<!> game over")
        print(f"winner: {state.players[state.turn_idx].name}")
        print([player.score for player in state.players])


if __name__ == "__main__":
    pass
