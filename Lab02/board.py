from typing import Optional
from settings import PLAYER_BLACK, PLAYER_WHITE
from helpers import validate_start_grid_values, generate_start_grid


class Board:
    def __init__(
        self,
        rows: int = 8,
        cols: int = 8,
        grid: Optional[list[list[str]]] = None,
        grid_state_str: Optional[str] = None,
        last_move: Optional[tuple[tuple[int, int], tuple[int, int]]] = None,
    ):
        self.last_move = last_move

        if grid is not None:
            grid_rows = len(grid)
            grid_cols = len(grid[0]) if grid_rows > 0 else 0
            validate_start_grid_values(grid_rows, grid_cols)

            self.rows = grid_rows
            self.cols = grid_cols
            self.grid = [row[:] for row in grid]

        elif grid_state_str is not None:
            lines = grid_state_str.strip().split("\n")
            state_grid = [line.strip().split() for line in lines]
            state_rows = len(state_grid)
            state_cols = len(state_grid[0]) if state_rows > 0 else 0
            validate_start_grid_values(state_rows, state_cols)

            self.rows = state_rows
            self.cols = state_cols
            self.grid = state_grid

        else:
            validate_start_grid_values(rows, cols)

            self.rows = rows
            self.cols = cols
            self.grid = generate_start_grid(rows, cols)

    def display(self) -> None:
        for row in self.grid:
            print(" ".join(row))

    def is_winner(self, player: str) -> bool:
        target_row = self.rows - 1 if player == PLAYER_BLACK else 0
        return any(cell == player for cell in self.grid[target_row])

    def get_winner(self) -> Optional[str]:
        if self.is_winner(PLAYER_BLACK):
            return PLAYER_BLACK
        elif self.is_winner(PLAYER_WHITE):
            return PLAYER_WHITE
        return None

    def is_game_over(self) -> bool:
        return self.get_winner() is not None
