import sys
from typing import Optional
from settings import PLAYER_BLACK, PLAYER_WHITE, LAST_MOVE_SIGN, BOARD_SPACE
from helpers import (
    validate_start_grid_values,
    generate_start_grid,
    validate_rows,
    validate_cols,
    validate_cell,
)


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

    def get_possible_moves(self, player: str) -> list[tuple[int, int], tuple[int, int]]:
        moves = []

        direction = 1 if player == PLAYER_BLACK else -1
        opponent = PLAYER_WHITE if player == PLAYER_BLACK else PLAYER_BLACK

        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == player:
                    curr_location = (r, c)
                    new_row = r + direction
                    new_col_1 = c - 1
                    new_col_2 = c + 1

                    if self.grid[new_row][c] not in [
                        player,
                        opponent,
                    ] and validate_rows(new_row, self.rows):
                        moves.append((curr_location, (new_row, c)))
                    if self.grid[new_row][new_col_1] != player and validate_cell(
                        new_row, new_col_1, self.rows, self.cols
                    ):
                        moves.append((curr_location, (new_row, new_col_1)))
                    if self.grid[new_row][new_col_2] != player and validate_cell(
                        new_row, new_col_2, self.rows, self.cols
                    ):
                        moves.append((curr_location, (new_row, new_col_2)))
        return moves

    def make_move(
        self, move: tuple[tuple[int, int], tuple[int, int]], player: str
    ) -> "Board":
        new_grid = [row[:] for row in self.grid]

        if self.last_move is not None:
            old_start_r, old_start_c = self.last_move[0]
            if new_grid[old_start_r][old_start_c] == LAST_MOVE_SIGN:
                new_grid[old_start_r][old_start_c] = BOARD_SPACE
        else:
            for r in range(self.rows):
                for c in range(self.cols):
                    if new_grid[r][c] == LAST_MOVE_SIGN:
                        new_grid[r][c] = BOARD_SPACE

        (start_r, start_c), (end_r, end_c) = move
        new_grid[start_r][start_c] = LAST_MOVE_SIGN
        new_grid[end_r][end_c] = player

        return Board(grid=new_grid, last_move=move)

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


def test():
    input_data = sys.stdin.read().strip()

    if not input_data:
        print("Błąd: Nie podano żadnych danych na wejściu.")
        return

    print("--- 1. Surowe dane wczytane z pliku ---")
    print(input_data)
    print("\n--- 2. Przekazanie do klasy Board i wywołanie display() ---")

    board = Board(grid_state_str=input_data)

    board.display()

    print(f"\nWymiary: {board.rows} wierszy, {board.cols} kolumn.")

    if getattr(board, "last_move", None):
        print(f"Wykryto zapamiętany ostatni ruch na wejściu.")

    new_board = board.make_move(((6, 0), (5, 0)), PLAYER_WHITE)
    new_board.display()


if __name__ == "__main__":
    test()
