from constants import *


# STAGE 1
def get_gem_at(board, row, col):
    if 0 <= row < BOARD_HEIGHT and 0 <= col < BOARD_WIDTH:
        return board[row][col]
    return None
