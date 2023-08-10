from stages.stage_1 import *


# STAGE 2
def find_matching_gems(board):
    gems_to_remove = []

    # loop through each space, checking for 3 adjacent identical gems
    for row in range(BOARD_HEIGHT):
        for col in range(BOARD_WIDTH):
            # look for vertical matches
            if get_gem_at(board, row, col) == get_gem_at(board, row + 1, col) == get_gem_at(board, row + 2, col):
                target_gem = board[row][col]
                offset = 0
                remove_set = []
                while get_gem_at(board, row + offset, col) == target_gem:
                    # keep checking if there's more than 3 gems in a row
                    remove_set.append((row + offset, col))
                    offset += 1
                gems_to_remove.append(remove_set)

            # look for vertical matches
            if get_gem_at(board, row, col) == get_gem_at(board, row, col + 1) == get_gem_at(board, row, col + 2):
                target_gem = board[row][col]
                offset = 0
                remove_set = []
                while get_gem_at(board, row, col + offset) == target_gem:
                    # keep checking, in case there's more than 3 gems in a row
                    remove_set.append((row, col + offset))
                    offset += 1
                gems_to_remove.append(remove_set)

    return gems_to_remove