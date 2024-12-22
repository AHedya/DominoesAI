from collections import Counter
import os
import yaml


def validate_direction():
    direction = None
    while direction == None:
        try:
            direction = input("Enter 'left' or 'right': ").lower().strip()[0]
        except:
            direction = None
        if direction not in ["left", "right", "r", "l"]:
            print("Invalid direction. Please try again.")
            direction = None
    return direction


def validate_idx(ui_tiles_length):
    idx = None
    while idx == None:
        try:
            idx = int(input("Enter index to play: "))
            if idx >= ui_tiles_length:
                idx = None
        except KeyboardInterrupt:
            print("goodbye")
            exit()
        except:
            continue
    return idx


def get_hand_frequency(player):
    hand_frequency = Counter()

    for tile in player:
        if tile.is_double():
            hand_frequency[tile.left] += 1
        else:
            hand_frequency[tile.left] += 1
            hand_frequency[tile.right] += 1
    return hand_frequency


def get_ground_frequency(state):
    ground_frequency = Counter()
    for tile in state:
        if tile.is_double():
            ground_frequency[tile.left] += 1
        else:
            ground_frequency[tile.left] += 1
            ground_frequency[tile.right] += 1
    return ground_frequency


def load_config(path):
    with open(path, "r") as file:
        return yaml.safe_load(file)


def cli_feedback(self, ui_tiles, rest_tiles):
    print("score:  ", end="")
    for i, player in enumerate(self.players):
        print(f"{player.name}: {self.scores[i]}  ", end="")
    print()
    print("======================")
    print(self.ground_tiles)
    print("======================")
    print("remaining tiles:  ", end="")
    for player in self.players:
        print(f"{player.name}: {len(player.hand)}  ", end="")
    print()
    print("\n your valid tiles")
    for i, tile in enumerate(ui_tiles):
        print(f"{i}: {tile}")
    for tile in rest_tiles:
        print(f"---{tile}")


if __name__ == "__main__":
    print(validate_idx(7))
