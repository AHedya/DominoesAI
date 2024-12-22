import numpy as np
import math


class Node:
    def __init__(
        self,
        game,
        args,
        state,
        parent=None,
        action_taken=None,
    ):
        self.game = game
        self.parent = parent
        self.args = args
        self.state = state
        self.action_taken = action_taken

        self.children = []
        self.expandable_moves = [
            i[1]
            for i in zip(
                [
                    any(condition)
                    for condition in game.get_valid_moves(
                        state.players[state.turn_idx], self.state.ground
                    )
                ],
                state.players[state.turn_idx].hand,
            )
            if i[0]
        ]

        self.visit_count = 0
        self.value_sum = 0

    def is_fully_expanded(self):
        return len(self.expandable_moves) == 0 and len(self.children) > 0

    def select(self):
        best_child = None
        best_ucb = -np.inf

        for child in self.children:
            ucb = self.get_ucb(child)
            if ucb > best_ucb:
                best_child = child
                best_ucb = ucb

            return best_child

    def get_ucb(self, child):
        q_value = child.value_sum / child.visit_count
        return q_value + self.args["C"] * math.sqrt(
            math.log(self.visit_count) / child.visit_count
        )

    def expand(self):
        action = np.random.choice(self.expandable_moves)
        self.expandable_moves.remove(action)
        child_state = self.state.copy()

        child_state = self.game.get_next_state(
            child_state, action, child_state.players[child_state.turn_idx]
        )

        ### instead of changing player(turn_idx), we keep the player, but change the state to another player state.
        ### as every player will tend to maximize it's hand
        # child_state = self.game.change_prespective(child_state,player=-1)
        child_state.change_turn()
        # play our action as player. and "rotate" the board for the opponen to play
        child = Node(self.game, self.args, child_state, self, action)
        self.children.append(child)
        return child

    def simulate(self):
        value, is_terminal = self.game.evaluate_state(self.state)
        if is_terminal:
            return value
        rollout_state = self.state.copy()
        while True:
            if rollout_state.turn_idx == 0:
                rollout_state.players[0].hand += rollout_state.tiles
            valid_moves = [
                i[1]
                for i in zip(
                    [
                        any(condition)
                        for condition in self.game.get_valid_moves(
                            rollout_state.players[rollout_state.turn_idx],
                            rollout_state.ground,
                        )
                    ],
                    rollout_state.players[rollout_state.turn_idx].hand,
                )
                if i[0]
            ]
            action = np.random.choice(valid_moves)
            rollout_state = self.game.get_next_state(
                rollout_state, action, rollout_state.players[rollout_state.turn_idx]
            )
            rollout_state.change_turn()
            value, is_terminal = self.game.evaluate_state(rollout_state)
            rollout_state.change_turn()
            if is_terminal:
                return value
            rollout_state.change_turn()

    def backpropagate(self, value):
        self.value_sum += value
        self.visit_count += 1
        if self.parent is not None:
            self.parent.backpropagate(value)


class MCTS:
    def __init__(self, game, args):
        self.game = game
        self.args = args
        if args.get("seed"):
            np.random.seed(args["seed"])

    def search(self, state):
        root = Node(self.game, self.args, state)
        for _ in range(self.args["num_searches"]):
            node = root
            # selection
            while node.is_fully_expanded():
                node = node.select()
            value, is_terminal = self.game.evaluate_state(node.state)
            # value = self.game.get_opponent_value(
            #     value
            # )  ##because children are always opponen moves
            if not is_terminal:
                # expansion
                node = node.expand()
                # simulation
                value = node.simulate()
            # backpropagation
            node.backpropagate(value)

        counts = np.array(
            [child.visit_count for child in root.children], dtype=np.float32
        )
        sum_visits = np.sum(counts, dtype=np.float64)
        counts /= sum_visits
        actions = [child.action_taken for child in root.children]
        action_probs = [i for i in zip(counts, actions)]
        return action_probs
