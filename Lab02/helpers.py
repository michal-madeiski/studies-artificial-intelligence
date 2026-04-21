from settings import PLAYER_BLACK, PLAYER_WHITE, BOARD_SPACE


def generate_start_grid(rows: int, cols: int) -> list[list[str]]:
    grid = []
    for i in range(rows):
        if i < 2:
            grid.append([PLAYER_BLACK] * cols)
        elif i >= (rows - 2):
            grid.append([PLAYER_WHITE] * cols)
        else:
            grid.append([BOARD_SPACE] * cols)
    return grid


def validate_start_grid_values(rows: int, cols: int) -> bool:
    if rows < 4 or cols < 4 or (rows != cols):
        raise ValueError("Invalid grid size: should be min. 4x4 square!")


def validate_rows(rows: int, board_rows: int) -> bool:
    return 0 <= rows < board_rows


def validate_cols(cols: int, board_cols: int) -> bool:
    return 0 <= cols < board_cols


def validate_cell(rows: int, cols: int, board_rows: int, board_cols: int) -> bool:
    return validate_rows(rows, board_rows) and validate_cols(cols, board_cols)


if __name__ == "__main__":
    test_rows, test_cols = 8, 8
    validate_start_grid_values(test_rows, test_cols)
    print(generate_start_grid(test_rows, test_cols))
