import pygame.sprite

#Creation of the class and its components - poses on the screen, arr of sprite sheet and its variables
class Bird(pygame.sprite.Sprite):
    def __init__(self, x_pos, y_pose):
        pygame.sprite.Sprite.__init__(self)
        self.images = [] # list of the images in the sprite sheet
        self.index = 0   # current location on the list
        self.counter = 0 # for the animation

        for i in range(1, 4): # loop on the images list
            img = pygame.image.load(f'Images/bird{i}.png') # loading the sprite
            self.images.append(img) # adding the image to the sprite sheet list on order
        self.image = self.images[self.index] # getting the index for each image
        self.rect = self.image.get_rect() # defining the boundaries of the bird
        self.rect.center = [x_pos, y_pose] # a center point of the bird
        self.vel = 0 # speed for moving up/down
        self.click = False # for the click of the player

    def update(self, game_over, flying):
        if game_over == False:
            if flying == True:

                self.vel += 0.5 # as the bird falls, its velocity increases, like gravity
                if self.vel > 8: # limiting the speed
                    self.vel = 8
                #print(self.vel)
                if self.rect.bottom < 504: # if the bird is still in the air, the fall will still get velocity
                    self.rect.y += int(self.vel)

                if pygame.mouse.get_pressed()[0] == 1 and self.click == False:
                    self.click = True
                    self.vel = -10
                if pygame.mouse.get_pressed()[0] == 0:
                    self.click = False

            #animation:
            self.counter += 1
            flap_cooldown = 5

            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]

            #rotate the bird
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)

        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)