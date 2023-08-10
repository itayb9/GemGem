import pygame
from pygame.locals import *
import random

from Classes.Bird import Bird
from Classes.Pipe import Pipe
from Classes.Button import Button

pygame.init()

clock = pygame.time.Clock()
fps = 60
###### SCREEN DISPLAY #####

screen_width = 600
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Flappy Bird")

#define game variables:
ground_scroll = 0
scroll_speed = 4
game_over = False
pipe_gap = 150
pipe_frequency = 1500
last_pipe = pygame.time.get_ticks() - pipe_frequency
pass_pipe = False
score = 0

#load the relevant images to the screen:
background = pygame.image.load('Images/bg.png.')
ground = pygame.image.load('Images/ground.png')
buttom_img = pygame.image.load('Images/restart.png')
start_img = pygame.image.load('Images/start_button.jpg')

font = pygame.font.SysFont('Bauhaus 93', 50)
text = font.render('Score: ', True, (255, 255, 255))
screen.blit(text, [30, 30])





def draw_text(text, font, color,x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

def reset_game():
    pipe_group.empty()
    john.rect.x = 100
    john.rect.y = int(screen_height / 2)
    score = 0
    return score



bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()
#Objects
john = Bird(100, int(screen_height / 2))
bird_group.add(john)
restart_button = Button(screen_width // 2 - 50, screen_height // 2 - 100, buttom_img)
start_button = Button(200,400, start_img)

flying = False
pre_start = True

run = True

####### GAME LOOP #######
while run:

    clock.tick(fps)
    #draw background:
    screen.blit(background, (0, 0))

    bird_group.draw(screen)
    bird_group.update(game_over, flying)
    pipe_group.draw(screen)
    if pre_start:
        start_button.draw(screen)
        start_font = pygame.font.SysFont('Bauhaus 93', 50)
        start_text = font.render('Flappy Bird', True, (255, 255, 255))
        screen.blit(start_text, [200, 200])



    screen.blit(ground, (ground_scroll, 504))

    if len(pipe_group) > 0:
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
            and bird_group.sprites()[0].rect.right > pipe_group.sprites()[0].rect.right and pass_pipe == False:
            pass_pipe = True
        if pass_pipe == True:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                pass_pipe = False
    draw_text(str(score), font, (255, 255, 255), int(screen_width / 2), 20)


    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or john.rect.top < 0:
        game_over = True

    if john.rect.bottom >= 504:
        game_over = True
        flying = False


    if game_over == False and flying == True and pre_start == False:

        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency:
            pipe_height = random.randint(-100, 100)
            bottom_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1, 150)
            top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1, 150)
            pipe_group.add(bottom_pipe, top_pipe)
            last_pipe = time_now
        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 35: # if the ground exceeds its limit, it resets its location
            ground_scroll = 0
        pipe_group.update(scroll_speed)


    if game_over == True:
        if restart_button.draw(screen) == True:
            game_over = False
            score = reset_game()




    ###### EVENT CHECKS ######

    for event in pygame.event.get(): # event check
        if event.type == pygame.QUIT: # quitting the game
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and flying == False and game_over == False and pre_start == False:
            flying = True
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if start_button.rect.topleft[0] <= pos[0] <= start_button.rect.topright[0] and start_button.rect.topleft[1] <= pos[1] <= start_button.rect.bottomleft[1]:
                pre_start = False
                flying = True

    pygame.display.update()
pygame.quit()