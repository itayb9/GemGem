from stages.stage_3 import *


def find_surrounding_neighbors(row, col):
    offsets = [(row + 1, col), (row - 1, col), (row, col + 1), (row, col - 1), (row - 1, col - 1), (row - 1, col + 1),
               (row + 1, col - 1), (row + 1, col + 1)]
    return offsets

def has_neighbors_in_location_sets(row, col, matched_gems):
    neighbor = find_surrounding_neighbors(row, col)
    for sequence in matched_gems:
        for index in sequence:
            if index in neighbor:
                return True
    return False
