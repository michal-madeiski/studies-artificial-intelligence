import sys
import time
from board import Board
from typing import Callable, Optional
from settings import PLAYER_WHITE, PLAYER_BLACK
from minimax import minimax


class GameController:
    def __init__(
        self,
        depth: int,
        heuristic_w: Callable[[Board, str], float],
        heuristic_b: Callable[[Board, str], float],
        grid_state_str: Optional[str] = None,
    ):
        self.board = Board(grid_state_str=grid_state_str)
        self.visited_nodes = [0]
        self.rounds = 0
        self.depth = depth
        self.heuristic_w = heuristic_w
        self.heuristic_b = heuristic_b

    def play(self):
        start_time = time.time()
        current_player = PLAYER_WHITE

        while not self.board.is_game_over():
            current_heuristic = self.heuristic_w if PLAYER_WHITE else self.heuristic_b

            best_move = minimax(
                self.board,
                self.depth,
                current_player,
                current_heuristic,
                self.visited_nodes,
            )

            self.board.display()
            print("." * 69)
            print(f"next move: {best_move[0]} -> {best_move[1]} [{current_player}]")
            print("=" * 69)

            self.board = self.board.make_move(best_move, current_player)
            self.rounds += 1
            current_player = (
                PLAYER_BLACK if current_player == PLAYER_WHITE else PLAYER_WHITE
            )

        execution_time = time.time() - start_time
        self.print_results(execution_time)

    def print_results(self, execution_time: float):
        print("=" * 25, "BREAKTHROUGH GAME", "=" * 25)
        self.board.display()
        print("." * 69)
        print(f"Winner: {self.board.get_winner()}")
        print(f"Rounds: {self.rounds}")
        print(
            f"Nodes: {self.visited_nodes[0]}",
            file=sys.stderr,
        )
        print(f"Time: {execution_time:.4f} s", file=sys.stderr)
        print("=" * 69)
