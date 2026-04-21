from board import Board
from typing import Callable
from settings import PLAYER_BLACK, PLAYER_WHITE


def minimax(
    board: Board,
    depth: int,
    player: str,
    heuristic: Callable[[Board, str], float],
    visited_nodes: list[int],
) -> tuple[tuple[int, int], tuple[int, int]]:
    visited_nodes[0] += 1

    best_move = None
    best_move_value = float("-inf")
    alpha = float("-inf")
    beta = float("inf")

    for move in board.get_possible_moves(player):
        new_board = board.make_move(move, player)

        move_value = minimax_inner(
            new_board, player, depth - 1, False, heuristic, alpha, beta, visited_nodes
        )

        if move_value > best_move_value:
            best_move_value = move_value
            best_move = move

    return best_move


def minimax_inner(
    board: Board,
    player: str,
    depth: int,
    is_maximizing: bool,
    heuristic: Callable[[Board, str], float],
    alpha: float,
    beta: float,
    visited_nodes: list[int],
) -> float:
    visited_nodes[0] += 1

    if board.is_game_over():
        return float("inf") if board.get_winner() == player else float("-inf")

    if depth == 0:
        return heuristic(board, player)

    opponent = PLAYER_WHITE if player == PLAYER_BLACK else PLAYER_BLACK

    current_player = player if is_maximizing else opponent
    possible_moves = board.get_possible_moves(current_player)

    if is_maximizing:
        best_move_value = float("-inf")

        for move in possible_moves:
            new_board = board.make_move(move, current_player)

            move_value = minimax_inner(
                new_board,
                player,
                depth - 1,
                False,
                heuristic,
                alpha,
                beta,
                visited_nodes,
            )

            alpha = max(alpha, move_value)
            if beta <= alpha:
                break

            best_move_value = max(best_move_value, move_value)
        return best_move_value
    else:
        best_move_value = float("inf")

        for move in possible_moves:
            new_board = board.make_move(move, current_player)

            move_value = minimax_inner(
                new_board,
                player,
                depth - 1,
                True,
                heuristic,
                alpha,
                beta,
                visited_nodes,
            )

            beta = min(beta, move_value)
            if beta <= alpha:
                break

            best_move_value = min(best_move_value, move_value)
        return best_move_value
