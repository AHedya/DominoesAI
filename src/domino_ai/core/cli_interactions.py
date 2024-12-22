from colorama import Fore, Style
import os

# Get terminal size
try:
    max_width = os.get_terminal_size().columns
except:
    max_width = 80

colors = [Fore.LIGHTGREEN_EX, Fore.LIGHTBLUE_EX]


def draw_box(content_list, style="thin"):
    content_str = "".join(
        [f"{colors[d.color]}{str(d)}{Style.RESET_ALL}" for d in content_list]
    )

    width = min(max_width, max(int(len(content_str) / 2.2) + 2, 10))
    if style == "bold":
        top_border = f"{Fore.YELLOW}{Style.BRIGHT}{'┏' + '━' * (width - 2) + '┓'}{Style.RESET_ALL}"
        bottom_border = f"{Fore.YELLOW}{Style.BRIGHT}{'┗' + '━' * (width - 2) + '┛'}{Style.RESET_ALL}"
        content_line = f"{Fore.YELLOW}{Style.BRIGHT}{Style.RESET_ALL} {content_str} {Fore.YELLOW}{Style.BRIGHT}{Style.RESET_ALL}"
    else:
        top_border = f"{Fore.YELLOW}{'┌' + '─' * (width - 2) + '┐'}{Style.RESET_ALL}"
        bottom_border = f"{Fore.YELLOW}{'└' + '─' * (width - 2) + '┘'}{Style.RESET_ALL}"
        content_line = f"{Fore.YELLOW}{Style.RESET_ALL} {content_str} {Fore.YELLOW}{Style.RESET_ALL}"

    print(top_border)
    print(content_line)
    print(bottom_border)


def draw_scores(players):
    for i, player in enumerate(players):
        print(f"{colors[i]}{player.name}{Style.RESET_ALL}: {player.score}  ", end="")


def draw_remaining_tiles(state):
    print("remaining tiles:")
    print(f"{Fore.YELLOW}outside{Style.RESET_ALL}: {len(state.tiles)} ", end="")
    for i, player in enumerate(state.players):
        print(
            f"| {colors[i]}{player.name}{Style.RESET_ALL}: {len(player.hand)} ", end=""
        )
    print()


def cli_feedback(state, print_status=True, main_player=None):
    """printing colorful feedback to user

    Args:
        state (DominoState): current domino state
        print_status (bool, optional):controls whether printing the feed back or not. Defaults to True.
        main_player (Player, optional): The player to whom feedback is performed. If None, defaults to player with index zero. Defaults to None.

    Returns:
        _type_: _description_
    """
    ## depends on game.get_valid_moves.
    if not print_status:
        return

    draw_scores(state.players)
    print()

    draw_box(state.ground)

    draw_remaining_tiles(state)

    if not main_player:
        main_player = state.players[0]
        for p in state.players:
            # compromises import <Player> type.
            if "player" in p.name:
                main_player = p
                break
        else:
            return

    ui_tiles = []
    rest_tiles = []
    for i in zip(main_player.hand, main_player.conditions):
        if any(i[1]):
            ui_tiles.append(i[0])
        else:
            rest_tiles.append(i[0])

    print("\n<!> your tiles")
    print(Fore.GREEN, end="")
    for i, tile in enumerate(ui_tiles):
        print(f"{i}: {tile}")
    print(Style.RESET_ALL, end="")

    print(Fore.RED, end="")
    for tile in rest_tiles:
        print(f"---{tile}")
    print(Style.RESET_ALL, end="")

    return ui_tiles


if __name__ == "__main__":
    pass
