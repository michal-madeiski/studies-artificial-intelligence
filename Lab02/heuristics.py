from board import Board
from helpers import validate_cell, validate_cols
from settings import PLAYER_BLACK, PLAYER_WHITE, BOARD_SPACE, LAST_MOVE_SIGN


def distance_to_win_strategy(board: Board, player: str) -> float:
    max_player_forward = 0
    max_opponent_forward = 0
    max_forward = board.rows - 1

    for r in range(board.rows):
        for c in range(board.cols):
            cell = board.grid[r][c]

            if cell in [BOARD_SPACE, LAST_MOVE_SIGN]:
                continue

            elif cell == PLAYER_BLACK:
                forward = r
                if player == PLAYER_BLACK:
                    max_player_forward = max(max_player_forward, forward)
                else:
                    max_opponent_forward = max(max_opponent_forward, forward)

            elif cell == PLAYER_WHITE:
                forward = max_forward - r
                if player == PLAYER_WHITE:
                    max_player_forward = max(max_player_forward, forward)
                else:
                    max_opponent_forward = max(max_opponent_forward, forward)

    score = (max_player_forward) * 3 - max_opponent_forward
    return float(score)


def pawn_count_strategy(board: Board, player: str) -> float:
    opponent = PLAYER_BLACK if player == PLAYER_WHITE else PLAYER_WHITE

    player_count = 0
    opponent_count = 0

    flat_board = [cell for row in board.grid for cell in row]

    player_count = flat_board.count(player)
    opponent_count = flat_board.count(opponent)

    score = player_count - opponent_count
    return float(score)


def threat_map_strategy(board: Board, player: str) -> float:
    opponent = PLAYER_WHITE if player == PLAYER_BLACK else PLAYER_BLACK

    player_free_kill = 0
    player_defended = 0
    opponent_free_kill = 0
    opponent_defended = 0

    for r in range(board.rows):
        for c in range(board.cols):
            cell = board.grid[r][c]

            if cell not in [PLAYER_BLACK, PLAYER_WHITE]:
                continue

            forward_direction = 1 if cell == PLAYER_BLACK else -1
            backward_direction = -1 if cell == PLAYER_BLACK else 1

            attackers = 0
            for left_right in [-1, 1]:
                attacker_row, attacker_col = r + forward_direction, c + left_right
                if (
                    validate_cell(attacker_row, attacker_col, board.rows, board.cols)
                    and board.grid[attacker_row][attacker_col] == opponent
                ):
                    attackers += 1

            defenders = 0
            for left_right in [-1, 1]:
                defender_row, defender_col = r + backward_direction, c + left_right
                if (
                    validate_cell(defender_row, defender_col, board.rows, board.cols)
                    and board.grid[defender_row][defender_col] == player
                ):
                    defenders += 1

            if attackers > 0:
                if cell == player:
                    if defenders == 0:
                        player_free_kill += 1
                    else:
                        player_defended += 1
                else:
                    if defenders == 0:
                        opponent_free_kill += 1
                    else:
                        opponent_defended += 1

    score = 0
    score -= player_free_kill * 3
    score -= player_defended
    score += opponent_free_kill * 3
    score += opponent_defended

    return float(score)
