from .core.domino_game import DominoGame
from .ai.ai_stratigies import (
    PlacementContext,
    MCTSStrategy,
    BlindStrategy,
    RuleBasedStrategy,
)
from .core.utils import load_config
from .parser import create_parser


def main():

    parser = create_parser()
    args = parser.parse_args()
    config = load_config("config.yaml")

    # Update configuration with command-line arguments
    for k, v in args.__dict__.items():
        if v:
            config[k] = v

    # initial game engine
    game = DominoGame(config["players"], config["seed"])

    ai_strategies = {
        "mcts": MCTSStrategy(game),
        "blind": BlindStrategy(game),
        "rule_based": RuleBasedStrategy(game),
    }
    placement_context = PlacementContext(ai_strategies[config["strategy"]])

    game.casual_game(placement_context, config["score"])


if __name__ == "__main__":
    main()
