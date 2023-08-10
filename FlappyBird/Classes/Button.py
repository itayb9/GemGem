import pygame.mouse


class Button():
    def __init__(self, x,y, img):
        self.img = img
        self.rect = self.img.get_rect()
        self.rect.topleft = (x, y)

    def draw(self, screen):
        action = False
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True
        screen.blit(self.img, (self.rect.x, self.rect.y))
        return action
