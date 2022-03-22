import pygame
from pygame.locals import *
import keyboard
import random

pygame.init()
clock = pygame.time.Clock()

# Dimensions
game_width = 800
game_height = 900

# creating game window
screen = pygame.display.set_mode((game_width, game_height))
pygame.display.set_caption("Flappy Bird")

# Background Images
background = pygame.image.load('img/bg.png')
ground = pygame.image.load('img/ground.png')
button_img = pygame.image.load('img/restart.png')
space_img = pygame.image.load('img/space.png')

# game variables
scroll = 0
speed = 4  # animation speed
flying = False
lose = False
gap = 80  # gap between pipes in pixels
pipe_freq = 1500  # milliseconds
last_pipe = pygame.time.get_ticks()  # time as soon as game starts
score = 0
passed_pipe = False
font = pygame.font.SysFont('Times', 60)
color = (41, 36, 33)  # black
transparent = (0, 0, 0, 0)
ground_axis = 750  # ground y-axis


# Making the bird
class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.count = 0  # speed of animation

        for num in range(1, 3):  # making flapping animation by cycling through different pictures
            img = pygame.image.load(f'img/bird{num}.png')
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False

    def update(self):

        # Falling Animation
        if flying == True:
            self.vel += 0.5

            # drop until it hits ground
            if self.rect.bottom < ground_axis:
                self.rect.y += int(self.vel)

        # Jumping Animation
        if keyboard.is_pressed("space") and self.clicked == False:
            self.clicked = True
            self.vel = -9  # makes bird fly up

        # Condition to make it only tap to move (cannot hold button)
        if not keyboard.is_pressed("space"):
            self.clicked = False

        # Flapping Animation
        self.count += 1
        flap_speed = 10

        if self.count > flap_speed:
            self.count = 0
            self.index += 1
            if self.index >= len(self.images):  # Goes back to the first picture after it reaches the end
                self.index = 0

        self.image = self.images[self.index]


class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/pipe.png')
        self.rect = self.image.get_rect()

        # postion 1 is Toppipe, -1 is bottompipe
        if pos == 1:
            # False = x-axis, True = y-axis
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - gap]  # places top pipe with gap

        if pos == -1:
            self.rect.topleft = [x, y + gap]  # places bottom pipe with gap

    def update(self):
        self.rect.x -= speed
        if self.rect.right < 0:
            self.kill()  # deletes pipe memory once it leaves screen


# Restart Button
class Button:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def click(self):

        click = False
        pos = pygame.mouse.get_pos()

        # check if mouse is over the button
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                click = True

        if keyboard.is_pressed("r") or keyboard.is_pressed("space"):
            click = True

        screen.blit(self.image, (self.rect.x, self.rect.y))

        return click


def reset_game():
    pipe_group.empty()  # clear pipes
    flappy.rect.x = 100  # places bird back to starting position
    flappy.rect.y = int(game_height / 2)
    score_num = 0  # score reset
    return score_num


# Displaying Score
def display_score(text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    screen.blit(img, (x, y))


# add bird to group to use sprite features
bird_group = pygame.sprite.Group()
flappy = Bird(100, int(game_height / 2))
bird_group.add(flappy)

# Create pipe group for pipe animation
pipe_group = pygame.sprite.Group()

# button
button = Button(game_width / 2 - 70, game_height / 2 - 70, button_img)

Game_Running = True
while Game_Running:

    clock.tick(80)  # 80 frames per second

    # Display background and ground images
    screen.blit(background, (0, 0))
    screen.blit(ground, (scroll, ground_axis))  # scroll is used to create moving ground

    # Add bird and pipe to screen
    bird_group.draw(screen)
    bird_group.update()
    pipe_group.draw(screen)
    screen.blit(space_img, (game_width / 2 - 100, game_height / 2 - 100))

    # Score
    if len(pipe_group) > 0:
        # Checks is bird has a passed a pipe
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left \
                and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right \
                and passed_pipe == False:
            passed_pipe = True

        if passed_pipe == True:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                passed_pipe = False

        display_score(str(score), font, color, int(game_width / 2), 20)

    # Checks if bird hits pipes or top or bottom of the screen
    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or \
            flappy.rect.top < 0 \
            or flappy.rect.bottom >= ground_axis:
        lose = True
        flying = False

    # Scroll continues as long as bird doesnt hit ground
    if lose == False and flying == True:
        # update scroll while bird flying to create moving floor
        scroll -= speed
        if abs(scroll) > 35:
            scroll = 0

        # Generating pipes for pipe animation
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_freq:
            pipe_height = random.randint(-100, 100)
            bottom_pipe = Pipe(game_width, int(game_height / 2) + pipe_height, -1)
            Top_pipe = Pipe(game_width, int(game_height / 2) + pipe_height, 1)
            pipe_group.add(bottom_pipe)
            pipe_group.add(Top_pipe)
            last_pipe = time_now

        pipe_group.update()

    # check for game over
    if lose == True:
        if button.click() == True:
            lose = False
            score = reset_game()

    # quiting menu
    for event in pygame.event.get():
        if event.type == pygame.QUIT or keyboard.is_pressed("esc"):
            Game_Running = False
        if (event.type == pygame.MOUSEBUTTONDOWN or keyboard.is_pressed("space")) and flying == False and lose == False:
            space_img.fill(transparent)  # Cover the space image
            flying = True

    pygame.display.update()

pygame.quit()
