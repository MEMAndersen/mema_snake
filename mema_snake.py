import sys
import pygame
import random
import numpy as np
import math

pygame.init()

clock = pygame.time.Clock()

col = {"black": (0, 0, 0),
       "white": (255, 255, 255),
       "dark_grey": (50, 50, 50)}

size = width, height = 640, 480
block_size = 10
grid_size_x = int(width / block_size) - 1
grid_size_y = int(height / block_size) - 1
run = True
directions = ('up', 'left', 'down', 'right')
valid_pos = [(5, 5)]

screen = pygame.display.set_mode(size)


class Entity:
    def __init__(self, grid_x, grid_y, size_x, size_y):
        self.x = grid_x * size_x
        self.y = grid_y * size_x
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.size_x = size_x
        self.size_y = size_y
        self.col = col["white"]

        # used for collision
        self.rect = pygame.Rect((self.x, self.y), (self.size_x, self.size_y))
        self.snap_to_grid()
        self.length = 1

    def snap_to_grid(self):
        dx = math.floor(self.rect.centerx / block_size)
        dy = math.floor(self.rect.centery / block_size)
        self.rect = pygame.Rect((block_size * dx, block_size * dy), (self.size_x, self.size_y))


class SnakePart(Entity):

    def __init__(self, grid_x, grid_y, part_dir, head=False):
        Entity.__init__(self, grid_x, grid_y, block_size, block_size)
        self.part_dir = part_dir
        self.head = head
        self.previous_dir = part_dir

    def draw(self):
        pygame.draw.rect(screen, self.col, self.rect)

    def move(self):

        if self.part_dir == 'up':
            self.rect = self.rect.move(0, -block_size)
        elif self.part_dir == 'left':
            self.rect = self.rect.move(-block_size, 0)
        elif self.part_dir == 'down':
            self.rect = self.rect.move(0, block_size)
        elif self.part_dir == 'right':
            self.rect = self.rect.move(block_size, 0)

        self.previous_dir = self.part_dir

        self.edges()

    def edges(self):
        if self.rect.centerx < 0:
            self.rect = self.rect.move(width, 0)
        elif self.rect.centerx > width:
            self.rect = self.rect.move(-width, 0)

        if self.rect.centery < 0:
            self.rect = self.rect.move(0, height)
        elif self.rect.centery > height:
            self.rect = self.rect.move(0, -height)


class Snake:
    def __init__(self):

        # movement
        self.move_delay = 400
        self.time_since_move = 0

        self.snake_parts = [SnakePart(5, 5, 'left', head=True),
                            SnakePart(6, 5, 'left'),
                            SnakePart(7, 5, 'left'),
                            SnakePart(8, 5, 'left')]

    def draw(self):
        for snake_part in self.snake_parts:
            snake_part.draw()

    def update_snake_head_dir(self):
        # Change direction of snake head by user input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and self.snake_parts[0].previous_dir != 'down':
            self.snake_parts[0].part_dir = 'up'
        if keys[pygame.K_LEFT] and self.snake_parts[0].previous_dir != 'right':
            self.snake_parts[0].part_dir = 'left'
        if keys[pygame.K_DOWN] and self.snake_parts[0].previous_dir != 'up':
            self.snake_parts[0].part_dir = 'down'
        if keys[pygame.K_RIGHT] and self.snake_parts[0].previous_dir != 'left':
            self.snake_parts[0].part_dir = 'right'

    def update_snake_body_dir(self):
        for i in range(len(self.snake_parts)-1, 0, -1):
            self.snake_parts[i].part_dir = self.snake_parts[i - 1].part_dir

    def move(self, dt):

        self.update_snake_head_dir()

        self.time_since_move += dt
        if self.time_since_move >= self.move_delay:
            # resetting time delay and moves
            self.time_since_move -= self.move_delay

            for snake_part in self.snake_parts:
                snake_part.move()
            self.update_snake_body_dir()

    def collision(self):
        for entity in entities[entities != self]:
            if self.rect.colliderect(entity.rect):
                self.food += 1


class Food(Entity):
    def __init__(self, valid_pos):
        grid_x, grid_y = random.choice(valid_pos)
        Entity.__init__(self, grid_x, grid_y, block_size, block_size)

    def draw(self):
        pygame.draw.circle(screen, self.col, self.rect.center, math.floor(block_size / 2))

    def move(self, dt):
        pass


def draw_entities():
    snake.draw()
    food.draw()


def draw_grid():
    for column in range(int(width / block_size + 1)):
        pygame.draw.line(screen, col["dark_grey"], (block_size * column, 0), (block_size * column, height), 1)
    for row in range(int(height / block_size + 1)):
        pygame.draw.line(screen, col["dark_grey"], (0, block_size * row), (width, block_size * row), 1)


def game_loop():
    while run:

        dt = clock.tick(60)
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

        # Move snake
        snake.move(dt)

        # Draw
        draw_grid()
        draw_entities()
        pygame.display.update()


if __name__ == '__main__':
    snake = Snake()
    food = Food(valid_pos)
    game_loop()

"""


    ballrect = ballrect.move(speed)
    if ballrect.left < 0 or ballrect.right > width:
        speed[0] = -speed[0]
    if ballrect.top < 0 or ballrect.bottom > height:
        speed[1] = -speed[1]

    screen.fill(black)
    screen.blit(ball, ballrect)
    pygame.display.flip()
"""
