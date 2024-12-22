from abc import ABC, abstractmethod

__all__ = ["PlacementContext", "BlindStrategy", "MCTSStrategy", "RuleBasedStrategy"]

import numpy as np
import os
import random

from ..core.domino_components import Player, AI_Player
from .mcts import MCTS
from ..core.utils import get_ground_frequency, get_hand_frequency, load_config


args = load_config(os.path.join(os.path.dirname(__file__), "hyper_parameters.yaml"))


class AIStrategy(ABC):
    @abstractmethod
    def get_domino_placement(self, hand, board):
        pass


class BlindStrategy(AIStrategy):
    """Blindly choose tile from valid hand tiles"""

    def __init__(self, game):
        self.game = game
        random.seed(args.get("blind_seed"))

    def get_domino_placement(self, state):
        valid_moves = [
            i[1]
            for i in zip(
                [
                    any(condition)
                    for condition in self.game.get_valid_moves(
                        state.players[state.turn_idx],
                        state.ground,
                    )
                ],
                state.players[state.turn_idx].hand,
            )
            if i[0]
        ]
        return random.choice(valid_moves)


class RuleBasedStrategy(AIStrategy):
    """ "Classic rule based strategy
    Experts are advised to perform evaluation, and return best probable tile placement
    """

    def __init__(self, game):
        self.game = game
        self.args = args["rule_based"]

    def get_domino_placement(self, state):
        ai = state.players[state.turn_idx]
        ai.double_ended_tile_score = None
        valid_tiles = [
            i[1]
            for i in zip(
                [
                    any(condition)
                    for condition in self.game.get_valid_moves(
                        ai,
                        state.ground,
                    )
                ],
                ai.hand,
            )
            if i[0]
        ]

        # prioritize value
        scores = [tile.count_tile() * self.args["tile_value"] for tile in valid_tiles]
        # prioritize doubles
        scores = [
            s * self.args["double_tiles"] if v.is_double() else s
            for v, s in zip(valid_tiles, scores)
        ]

        # prioritize versatility
        valid_tiles_conditions = [
            condition for condition in ai.conditions if any(condition)
        ]
        hand_frequency = get_hand_frequency(ai.hand)
        for idx, condition in enumerate(valid_tiles_conditions):
            if all(condition):
                playing_left = hand_frequency[valid_tiles[idx].left]
                playing_right = hand_frequency[valid_tiles[idx].right]
                ai.double_ended_tile_score = [
                    playing_left * self.args["tiles_in_hand"],
                    playing_right * self.args["tiles_in_hand"],
                ]
                continue
            elif condition[0]:
                coef = hand_frequency[valid_tiles[idx].left]
            elif condition[1]:
                coef = hand_frequency[valid_tiles[idx].right]
            scores[idx] += coef * self.args["tiles_in_hand"]

        # prtioritize playing safe
        ground_frequency = get_ground_frequency(state.ground)
        for idx, condition in enumerate(valid_tiles_conditions):
            if all(condition):
                playing_left = hand_frequency[valid_tiles[idx].right]
                playing_right = hand_frequency[valid_tiles[idx].left]
                ai.double_ended_tile_score[0] -= (
                    playing_left * self.args["tiles_in_ground"]
                )
                ai.double_ended_tile_score[1] -= (
                    playing_right * self.args["tiles_in_ground"]
                )
                continue

            elif condition[0]:
                coef = ground_frequency[valid_tiles[idx].right]
            elif condition[1]:
                coef = ground_frequency[valid_tiles[idx].left]
            scores[idx] -= coef * self.args["tiles_in_ground"]

        if ai.memory:
            for idx, condition in enumerate(valid_tiles_conditions):
                if condition[0]:
                    tile_half = valid_tiles[idx].left
                elif condition[1]:
                    tile_half = valid_tiles[idx].right
                if tile_half in ai.memory:
                    scores[idx] += self.args["blocking_bonus"]

        if ai.double_ended_tile_score:
            ai.double_ended_tile_score = (
                "l"
                if ai.double_ended_tile_score[0] >= ai.double_ended_tile_score[1]
                else "r"
            )
        action = valid_tiles[np.argmax(scores)]
        return action


class MCTSStrategy(AIStrategy):
    """Monte Carlo Tree Search (MCTS) Strategy.
    This implementation focuses on minimizing the AI player's remaining tiles by identifying the most probable optimal moves. Future enhancements will incorporate more advanced evaluation methods, leveraging the AI player's memory feature for improved decision-making.
    """

    def __init__(self, game):
        self.mcts = MCTS(game, args["mcts"])

    def get_domino_placement(self, state):
        if not state.ground:
            ai_player = state.players[state.turn_idx]
            action = ai_player.hand[
                max(
                    enumerate([tile.count_tile() for tile in ai_player.hand]),
                    key=lambda x: x[1],
                )[0]
            ]
            return action

        ai_state = state.copy()
        ai_state.turn_idx = 1
        for i, p_player in enumerate(ai_state.players):
            if type(p_player) == Player:
                new_player = AI_Player(f"ai {i}", p_player.hand)
                ai_state.players[i] = new_player

        mcts_probs = self.mcts.search(ai_state)
        action = mcts_probs[np.argmax([i[0] for i in mcts_probs])][1]
        return action


class AlphaBetaMiniMax(AIStrategy):
    """Alpha-Beta MiniMax strategy for AI"""

    def get_domino_placement(self, state):
        raise NotImplementedError("Alpha-beta hasn't yet implemented")


class PlacementContext:
    def __init__(self, strategy: AIStrategy):
        self.strategy = strategy

    def set_strategy(self, strategy: AIStrategy):
        self.strategy = strategy

    def calc(self, *args):
        return self.strategy.get_domino_placement(*args)
