import argparse
import sys
from game_controller import GameController
from heuristics import (
    distance_to_win_strategy,
    threat_map_strategy,
    pawn_count_strategy,
)


def main():
    parser = argparse.ArgumentParser(
        description="Breakthrough game settings",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "-d",
        type=int,
        required=True,
        help="game tree search depth",
    )

    heuristic_help = (
        "1 - pawn count\n" "2 - distance to win\n" "3 - threat map strategy"
    )

    parser.add_argument(
        "-hw",
        type=int,
        choices=[1, 2, 3],
        required=True,
        help=f"heuristic for W player:\n{heuristic_help}",
    )

    parser.add_argument(
        "-hb",
        type=int,
        choices=[1, 2, 3],
        required=True,
        help=f"heuristic for B player:\n{heuristic_help}",
    )

    args = parser.parse_args()

    board_data = None
    if not sys.stdin.isatty():
        board_data = sys.stdin.read().strip()
        if not board_data:
            board_data = None

    heuristics_map = {
        1: pawn_count_strategy,
        2: distance_to_win_strategy,
        3: threat_map_strategy,
    }

    depth = args.d
    hw = heuristics_map[args.hw]
    hb = heuristics_map[args.hb]

    game = GameController(depth, hw, hb, grid_state_str=board_data)
    game.play()


if __name__ == "__main__":
    main()
