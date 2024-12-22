import argparse


def create_parser():
    parser = argparse.ArgumentParser(description="Dominoes Game")
    parser.add_argument("--score", type=int, help="score at which game is over.")
    parser.add_argument(
        "--players",
        nargs=2,
        type=str,
        help='Enter names of players."player" must be contained in user name, and "ai" also must be contained in AI player name.',
    )
    parser.add_argument(
        "--strategy",
        choices=["blind", "rule_based", "mcts"],
        help="the strategy AI will use to play.",
    )
    parser.add_argument("--seed", type=int, help="setting seed for replication")

    return parser
