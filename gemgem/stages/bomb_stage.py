from stages.obstacle_stage import *


def get_local_bomb_gems_to_remove(board, row, col):
    """
       This function return a list of the gems to remove after the local bomb
       :param board: the board game
       :param row, col: location of the bomb gem after swap
       :return: list of the neighbors locations on board
    """
    return []


def get_new_board(board, matched_gems):
    """
        This function returns the updated board after moving away the matched gems locations
        :param matched_gems: the matched gems to remove.
        :param board: the game board
        :return: the updated board
    """


def get_color_bomb_gems_to_remove(board, target_gem_kind):
    """
    This function gets go over the board and returns a list of all the identical gems to the target
    :param board: the board game
    :param target_gem_kind: the number of the targeted gem
    :return: list of gems to remove
    """
    return []
