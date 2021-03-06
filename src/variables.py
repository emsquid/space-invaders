import pygame

WIDTH, HEIGHT = 1000, 750
SIDE_WIDTH = 275
GAME_WIDTH, GAME_HEIGHT = WIDTH - SIDE_WIDTH, HEIGHT
N_INVADERS = 6
N_STARS = 200
BLACK = (0, 0, 0)
INACTIVE_GREY = (200, 200, 200, 60)
WHITE = (255, 255, 255)
RED = (233, 30, 99)
GREEN = (30, 233, 99)
BLUE = (30, 99, 233)
PURPLE = (71, 91, 202)
PORT = 1313
CONTROLS = {
    "enter": pygame.K_RETURN,
    "left": pygame.K_LEFT,
    "right": pygame.K_RIGHT,
    "up": pygame.K_UP,
    "down": pygame.K_DOWN,
    "shoot": pygame.K_SPACE,
}
