# Gemgem (a Bejeweled clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

"""
This program has "gem data structures", which are basically dictionaries
with the following keys:
  'x' and 'y' - The location of the gem on the board. 0,0 is the top left.
                There is also a ROWABOVEBOARD row that 'y' can be set to,
                to indicate that it is above the board.
  'direction' - one of the four constant variables UP, DOWN, LEFT, RIGHT.
                This is the direction the gem is moving.
  'imageNum'  - The integer index into GEMIMAGES to denote which image
                this gem uses.
"""
import itertools
import random, time, pygame, sys, copy
from pygame.locals import *
from stages.obstacle_stage import *
from constants import *


def run_game():
    # Plays through a single game. When the game is over, this function returns.

    # initialize the board
    game_board = get_blank_board()
    game_board = initialize_board()
    score = 0
    fill_board_and_animate(game_board, [], score)  # Drop the initial gems.

    # initialize variables for the start of a new game
    first_selected_gem = None
    last_mouse_down_x = None
    last_mouse_down_y = None
    game_is_over = False
    last_score_deduction = time.time()
    click_continue_text_surf = None
    num_of_sleep_obstacles = 0

    while True:
        clicked_space = None
        for event in pygame.event.get():  # event handling loop
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == KEYUP and event.key == K_BACKSPACE:
                return  # start a new game

            elif event.type == MOUSEBUTTONUP:
                if game_is_over:
                    return  # after games ends, click to start a new game

                if event.pos == (last_mouse_down_x, last_mouse_down_y):
                    # This event is a mouse click, not the end of a mouse drag.
                    clicked_space = check_for_gem_click(event.pos)
                else:
                    # this is the end of a mouse drag
                    first_selected_gem = check_for_gem_click((last_mouse_down_x, last_mouse_down_y))
                    clicked_space = check_for_gem_click(event.pos)
                    if not first_selected_gem or not clicked_space:
                        # if not part of a valid drag, deselect both
                        first_selected_gem = None
                        clicked_space = None
            elif event.type == MOUSEBUTTONDOWN:
                # this is the start of a mouse click or mouse drag
                last_mouse_down_x, last_mouse_down_y = event.pos

        if clicked_space and not first_selected_gem:
            # This was the first gem clicked on.
            first_selected_gem = clicked_space
        elif clicked_space and first_selected_gem:
            # Two gems have been clicked on and selected. Swap the gems.
            first_swapping_gem, second_swapping_gem = get_swapping_gems(game_board, first_selected_gem, clicked_space)
            if first_swapping_gem is None and second_swapping_gem is None:
                # If both are None, then the gems were not adjacent
                first_selected_gem = None  # deselect the first gem
                continue

            # Show the swap animation on the screen.
            board_copy = get_board_copy_minus_gems(game_board, (first_swapping_gem, second_swapping_gem))
            animate_moving_gems(board_copy, [first_swapping_gem, second_swapping_gem], [], score)

            # Swap the gems in the board data structure.
            game_board[first_swapping_gem['x']][first_swapping_gem['y']] = second_swapping_gem['imageNum']
            game_board[second_swapping_gem['x']][second_swapping_gem['y']] = first_swapping_gem['imageNum']

            # See if this is a matching move.
            matched_gems = get_switched_matrix(find_matching_gems(get_switched_board(game_board)))

            # Check if the game is over
            hit_mad_obstacles = get_hit_obstacles(get_switched_board(game_board),
                                                  get_switched_matrix(matched_gems),
                                                  MAD_OBSTACLE)
            if hit_mad_obstacles:
                game_is_over = True

            # BONUS 3 See if there is a match that is next to the sleeping obstacle
            mad_obstacles = get_switched_list(get_hit_obstacles(get_switched_board(game_board),
                                                                get_switched_matrix(matched_gems),
                                                                SLEEP_OBSTACLE))
            if mad_obstacles:
                for obst in mad_obstacles:
                    game_board[obst[0]][obst[1]] = MAD_OBSTACLE

            if not matched_gems:
                # Was not a matching move; swap the gems back
                GAME_SOUNDS['bad swap'].play()
                animate_moving_gems(board_copy, [first_swapping_gem, second_swapping_gem], [], score)
                game_board[first_swapping_gem['x']][first_swapping_gem['y']] = first_swapping_gem['imageNum']
                game_board[second_swapping_gem['x']][second_swapping_gem['y']] = second_swapping_gem['imageNum']
            else:
                # This was a matching move.
                score_add = 0
                while matched_gems:
                    # Remove matched gems, then pull down the board.

                    # points is a list of dicts that tells fillBoardAndAnimate()
                    # where on the screen to display text to show how many
                    # points the player got. points is a list because if
                    # the player gets multiple matches, then multiple points text should appear.
                    points = []
                    for gemSet in matched_gems:
                        score_add += (10 + (len(gemSet) - 3) * 10)
                        for gem in gemSet:
                            game_board[gem[0]][gem[1]] = EMPTY_SPACE
                        points.append({'points': score_add,
                                       'x': gem[0] * GEM_IMAGE_SIZE + X_MARGIN,
                                       'y': gem[1] * GEM_IMAGE_SIZE + Y_MARGIN})

                    random.choice(GAME_SOUNDS['match']).play()
                    score += score_add

                    # BONUS - Put the sleep obstacle
                    if score > SLEEP_OBSTACLE_POINTS_NUM and num_of_sleep_obstacles < 2:
                        game_board[gem[0]][0] = SLEEP_OBSTACLE
                        num_of_sleep_obstacles += 1

                    # Drop the new gems.
                    fill_board_and_animate(game_board, points, score)

                    # Check if there are any new matches.
                    matched_gems = get_switched_matrix(find_matching_gems(get_switched_board(game_board)))
            first_selected_gem = None

            if not can_make_move(get_switched_board(game_board)):
                game_is_over = True

        # Draw the board.
        DISPLAY_SURF.fill(BG_COLOR)
        draw_board(game_board)
        if first_selected_gem is not None:
            highlight_space(first_selected_gem['x'], first_selected_gem['y'])
        if game_is_over:
            if click_continue_text_surf is None:
                # Only render the text once. In future iterations, just
                # use the Surface object already in click_continue_text_surf
                click_continue_text_surf = BASIC_FONT.render('Final Score: %s (Click to continue)' % (score), 1,
                                                             GAME_OVER_COLOR, GAME_OVER_BG_COLOR)
                clickContinueTextRect = click_continue_text_surf.get_rect()
                clickContinueTextRect.center = int(WINDOW_WIDTH / 2), int(WINDOW_HEIGHT / 2)
            DISPLAY_SURF.blit(click_continue_text_surf, clickContinueTextRect)
        elif score > 0 and time.time() - last_score_deduction > DEDUCT_SPEED:
            # score drops over time
            score -= 1
            last_score_deduction = time.time()
        draw_score(score)
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def get_swapping_gems(board, first_xy, second_xy):
    # If the gems at the (X, Y) coordinates of the two gems are adjacent,
    # then their 'direction' keys are set to the appropriate direction
    # value to be swapped with each other.
    # Otherwise, (None, None) is returned.
    first_gem = {'imageNum': board[first_xy['x']][first_xy['y']],
                 'x': first_xy['x'],
                 'y': first_xy['y']}
    second_gem = {'imageNum': board[second_xy['x']][second_xy['y']],
                  'x': second_xy['x'],
                  'y': second_xy['y']}

    if first_gem['x'] == second_gem['x'] + 1 and first_gem['y'] == second_gem['y']:
        first_gem['direction'] = LEFT
        second_gem['direction'] = RIGHT
    elif first_gem['x'] == second_gem['x'] - 1 and first_gem['y'] == second_gem['y']:
        first_gem['direction'] = RIGHT
        second_gem['direction'] = LEFT
    elif first_gem['y'] == second_gem['y'] + 1 and first_gem['x'] == second_gem['x']:
        first_gem['direction'] = UP
        second_gem['direction'] = DOWN
    elif first_gem['y'] == second_gem['y'] - 1 and first_gem['x'] == second_gem['x']:
        first_gem['direction'] = DOWN
        second_gem['direction'] = UP
    else:
        # These gems are not adjacent and can't be swapped.
        return None, None
    return first_gem, second_gem


def get_blank_board():
    # Create and return a blank board data structure.
    board = []
    for x in range(BOARD_WIDTH):
        board.append([EMPTY_SPACE] * BOARD_HEIGHT)
    return board


def draw_moving_gem(gem, progress):
    # Draw a gem sliding in the direction that its 'direction' key
    # indicates. The progress parameter is a number from 0 (just
    # starting) to 100 (slide complete).
    move_x = 0
    move_y = 0
    progress *= 0.01

    if gem['direction'] == UP:
        move_y = -int(progress * GEM_IMAGE_SIZE)
    elif gem['direction'] == DOWN:
        move_y = int(progress * GEM_IMAGE_SIZE)
    elif gem['direction'] == RIGHT:
        move_x = int(progress * GEM_IMAGE_SIZE)
    elif gem['direction'] == LEFT:
        move_x = -int(progress * GEM_IMAGE_SIZE)

    base_x = gem['x']
    base_y = gem['y']
    if base_y == ROW_ABOVE_BOARD:
        base_y = -1

    pixel_x = X_MARGIN + (base_x * GEM_IMAGE_SIZE)
    pixel_y = Y_MARGIN + (base_y * GEM_IMAGE_SIZE)
    r = pygame.Rect((pixel_x + move_x, pixel_y + move_y, GEM_IMAGE_SIZE, GEM_IMAGE_SIZE))
    DISPLAY_SURF.blit(GEM_IMAGES[gem['imageNum']], r)


def initialize_board():
    possible_gems = list(range(NUM_GEM_IMAGES))
    # Create and return a blank board data structure.
    board = []
    for x in range(BOARD_WIDTH):
        board.append([EMPTY_SPACE] * BOARD_HEIGHT)
    return board


def pull_down_all_gems(board):
    # pulls down gems on the board to the bottom to fill in any gaps
    for x in range(BOARD_WIDTH):
        gems_in_column = []
        for y in range(BOARD_HEIGHT):
            if board[x][y] != EMPTY_SPACE:
                gems_in_column.append(board[x][y])
        board[x] = ([EMPTY_SPACE] * (BOARD_HEIGHT - len(gems_in_column))) + gems_in_column


def get_drop_slots(board):
    # Creates a "drop slot" for each column and fills the slot with a
    # number of gems that that column is lacking. This function assumes
    # that the gems have been gravity dropped already.
    board_copy = copy.deepcopy(board)
    pull_down_all_gems(board_copy)

    drop_slots = []
    for i in range(BOARD_WIDTH):
        drop_slots.append([])

    # count the number of empty spaces in each column on the board
    for x in range(BOARD_WIDTH):
        for y in range(BOARD_HEIGHT - 1, -1, -1):  # start from bottom, going up
            if board_copy[x][y] == EMPTY_SPACE:
                possible_gems = list(range(NUM_GEM_IMAGES))
                for offset_x, offset_y in ((0, -1), (1, 0), (0, 1), (-1, 0)):
                    # Narrow down the possible gems we should put in the
                    # blank space so we don't end up putting two of
                    # the same gems next to each other when they drop.
                    neighbor_gem = get_gem_at(get_switched_board(board_copy), y + offset_y, x + offset_x)

                    if neighbor_gem is not None and neighbor_gem in possible_gems:
                        possible_gems.remove(neighbor_gem)

                new_gem = random.choice(possible_gems)
                board_copy[x][y] = new_gem
                drop_slots[x].append(new_gem)
    return drop_slots


def highlight_space(x, y):
    pygame.draw.rect(DISPLAY_SURF, HIGHLIGHT_COLOR, BOARD_RECTS[x][y], 4)


def get_dropping_gems(board):
    # Find all the gems that have an empty space below them
    board_copy = copy.deepcopy(board)
    dropping_gems = []
    for x in range(BOARD_WIDTH):
        for y in range(BOARD_HEIGHT - 2, -1, -1):
            if board_copy[x][y + 1] == EMPTY_SPACE and board_copy[x][y] != EMPTY_SPACE:
                # This space drops if not empty but the space below it is
                dropping_gems.append({'imageNum': board_copy[x][y], 'x': x, 'y': y, 'direction': DOWN})
                board_copy[x][y] = EMPTY_SPACE
    return dropping_gems


def animate_moving_gems(board, gems, points_text, score):
    # pointsText is a dictionary with keys 'x', 'y', and 'points'
    progress = 0  # progress at 0 represents beginning, 100 means finished.
    while progress < 100:  # animation loop
        DISPLAY_SURF.fill(BG_COLOR)
        draw_board(board)
        for gem in gems:  # Draw each gem.
            draw_moving_gem(gem, progress)
        draw_score(score)
        for point_text in points_text:
            points_surf = BASIC_FONT.render(str(point_text['points']), 1, SCORE_COLOR)
            points_rect = points_surf.get_rect()
            points_rect.center = (point_text['x'], point_text['y'])
            DISPLAY_SURF.blit(points_surf, points_rect)

        pygame.display.update()
        FPSCLOCK.tick(FPS)
        progress += MOVE_RATE  # progress the animation a little bit more for the next frame


def move_gems(board, moving_gems):
    # movingGems is a list of dicts with keys x, y, direction, imageNum
    for gem in moving_gems:
        if gem['y'] != ROW_ABOVE_BOARD:
            board[gem['x']][gem['y']] = EMPTY_SPACE
            move_x = 0
            move_y = 0
            if gem['direction'] == LEFT:
                move_x = -1
            elif gem['direction'] == RIGHT:
                move_x = 1
            elif gem['direction'] == DOWN:
                move_y = 1
            elif gem['direction'] == UP:
                move_y = -1
            board[gem['x'] + move_x][gem['y'] + move_y] = gem['imageNum']
        else:
            # gem is located above the board (where new gems come from)
            board[gem['x']][0] = gem['imageNum']  # move to top row


def fill_board_and_animate(board, points, score):
    drop_slots = get_drop_slots(board)
    while drop_slots != [[]] * BOARD_WIDTH:
        # do the dropping animation as long as there are more gems to drop
        moving_gems = get_dropping_gems(board)
        for x in range(len(drop_slots)):
            if len(drop_slots[x]) != 0:
                # cause the lowest gem in each slot to begin moving in the DOWN direction
                moving_gems.append({'imageNum': drop_slots[x][0], 'x': x, 'y': ROW_ABOVE_BOARD, 'direction': DOWN})

        board_copy = get_board_copy_minus_gems(board, moving_gems)
        animate_moving_gems(board_copy, moving_gems, points, score)
        move_gems(board, moving_gems)

        # Make the next row of gems from the drop slots
        # the lowest by deleting the previous lowest gems.
        for x in range(len(drop_slots)):
            if len(drop_slots[x]) == 0:
                continue
            board[x][0] = drop_slots[x][0]
            del drop_slots[x][0]


def check_for_gem_click(pos):
    # See if the mouse click was on the board
    for x in range(BOARD_WIDTH):
        for y in range(BOARD_HEIGHT):
            if BOARD_RECTS[x][y].collidepoint(pos[0], pos[1]):
                return {'x': x, 'y': y}
    return None  # Click was not on the board.


def draw_board(board):
    for x in range(BOARD_WIDTH):
        for y in range(BOARD_HEIGHT):
            pygame.draw.rect(DISPLAY_SURF, GRID_COLOR, BOARD_RECTS[x][y], 1)
            gem_to_draw = board[x][y]
            if gem_to_draw != EMPTY_SPACE:
                DISPLAY_SURF.blit(GEM_IMAGES[gem_to_draw], BOARD_RECTS[x][y])


def get_board_copy_minus_gems(board, gems):
    # Creates and returns a copy of the passed board data structure,
    # with the gems in the "gems" list removed from it.
    #
    # Gems is a list of dicts, with keys x, y, direction, imageNum

    board_copy = copy.deepcopy(board)

    # Remove some of the gems from this board data structure copy.
    for gem in gems:
        if gem['y'] != ROW_ABOVE_BOARD:
            board_copy[gem['x']][gem['y']] = EMPTY_SPACE
    return board_copy


def draw_score(score):
    score_img = BASIC_FONT.render(str(score), 1, SCORE_COLOR)
    score_rect = score_img.get_rect()
    score_rect.bottomleft = (10, WINDOW_HEIGHT - 6)
    DISPLAY_SURF.blit(score_img, score_rect)


# Get mat with rows first and then cols
def get_switched_board(mat):
    mat_copy = copy.deepcopy(mat)
    new_board = list(map(list, itertools.zip_longest(*mat_copy, fillvalue=None)))
    return new_board


# Change the X and Y in list of lists
def get_switched_matrix(matrix):
    new_matrix = []
    for match in matrix:
        switched_match = get_switched_list(match)
        new_matrix.append(switched_match)
    return new_matrix


# Change X and Y in a list
def get_switched_list(list_to_switch):
    return [(t[1], t[0]) for t in list_to_switch]


def load_images():
    gem_images = []

    for i in range(1, NUM_GEM_IMAGES + 1):
        gem_image = pygame.image.load('../images/gem%s.png' % i)
        if gem_image.get_size() != (GEM_IMAGE_SIZE, GEM_IMAGE_SIZE):
            gem_image = pygame.transform.smoothscale(gem_image, (GEM_IMAGE_SIZE, GEM_IMAGE_SIZE))
        gem_images.append(gem_image)

    sleep_obstacle_image = pygame.image.load('../images/sleep.png')
    sleep_obstacle_image = pygame.transform.smoothscale(sleep_obstacle_image, (GEM_IMAGE_SIZE, GEM_IMAGE_SIZE))
    gem_images.append(sleep_obstacle_image)

    mad_obstacle_image = pygame.image.load('../images/mad.png')
    mad_obstacle_image = pygame.transform.smoothscale(mad_obstacle_image, (GEM_IMAGE_SIZE, GEM_IMAGE_SIZE))
    gem_images.append(mad_obstacle_image)

    return gem_images


def get_hit_obstacles(board, matched_gems, obstacle_type):
    hit_obstacles = []

    # Find the obstacle location on the board
    for row_index in range(BOARD_HEIGHT):
        for col_index in range(BOARD_WIDTH):
            if get_gem_at(board, row_index, col_index) == obstacle_type:
                # Check if there is a set next to the obstacle
                if has_neighbors_in_location_sets(row_index, col_index, matched_gems):
                    hit_obstacles.append((row_index, col_index))

    return hit_obstacles


def main():
    global FPSCLOCK, DISPLAY_SURF, GEM_IMAGES, GAME_SOUNDS, BASIC_FONT, BOARD_RECTS

    # Initial set up.
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAY_SURF = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Gemgem')
    BASIC_FONT = pygame.font.Font('freesansbold.ttf', 36)
    GEM_IMAGES = load_images()

    # Load the sounds.
    GAME_SOUNDS = {'bad swap': pygame.mixer.Sound('../sounds/badswap.wav'), 'match': []}
    for i in range(NUM_MATCH_SOUNDS):
        GAME_SOUNDS['match'].append(pygame.mixer.Sound('../sounds/match%s.wav' % i))

    # Create pygame.Rect objects for each board space to
    # do board-coordinate-to-pixel-coordinate conversions.
    BOARD_RECTS = []
    for x in range(BOARD_WIDTH):
        BOARD_RECTS.append([])
        for y in range(BOARD_HEIGHT):
            r = pygame.Rect((X_MARGIN + (x * GEM_IMAGE_SIZE),
                             Y_MARGIN + (y * GEM_IMAGE_SIZE),
                             GEM_IMAGE_SIZE,
                             GEM_IMAGE_SIZE))
            BOARD_RECTS[x].append(r)

    while True:
        run_game()


main()
