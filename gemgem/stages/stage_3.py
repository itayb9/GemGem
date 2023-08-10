from stages.stage_2 import *


# STAGE 3
def check_patterns(board, row, col, patterns):
    for pattern in patterns:
        if get_gem_at(board, pattern[0][0] + row, pattern[0][1] + col) == get_gem_at(board, pattern[1][0] + row,
                                                                                     pattern[1][1] + col) == get_gem_at(
                board, pattern[2][0] + row, pattern[2][1] + col):
            return True
    return False


def can_make_move(board):
    patterns = (((0, 1), (1, 0), (2, 0)),
                ((0, 1), (1, 1), (2, 0)),
                ((0, 0), (1, 1), (2, 0)),
                ((0, 1), (1, 0), (2, 1)),
                ((0, 0), (1, 0), (2, 1)),
                ((0, 0), (1, 1), (2, 1)),
                ((0, 0), (0, 2), (0, 3)),
                ((0, 0), (0, 1), (0, 3)),
                ((1, 0), (0, 1), (0, 2)),
                ((1, 0), (1, 1), (0, 2)),
                ((0, 0), (1, 1), (0, 2)),
                ((1, 0), (0, 1), (1, 2)),
                ((0, 0), (0, 1), (1, 2)),
                ((0, 0), (1, 1), (1, 2)),
                ((0, 0), (2, 0), (3, 0)),
                ((0, 0), (1, 0), (3, 0)))
    for i in range(BOARD_HEIGHT):
        for j in range(BOARD_WIDTH):
            if check_patterns(board, i, j, patterns):
                return True
    return False

# board = [
#     [1, 2, 3],
#     [4, 5, 6],
#     [7, 8, 9]
# ]
# pattern = [(1, 2), (0, 1), (2, 2)]
# print(board[pattern[0][0]][pattern[0][1]])
# print(board[pattern[1][0]][pattern[1][1]])
# print(board[pattern[2][0]][pattern[2][1]])
# # location = (1, 2)
# i = 0
# j = 1
# # print(board[location[0]][location[1]])
# # print(board[i][j])
