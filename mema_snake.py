import sys
import pygame
import random
import math
import numpy as np

pygame.init()

clock = pygame.time.Clock()

col = {"black": (0, 0, 0),
       "white": (255, 255, 255),
       "dark_grey": (50, 50, 50)}

size = width, height = 640, 480
block_size = 10
grid_size_x = int(width / block_size)
grid_size_y = int(height / block_size)

screen = pygame.display.set_mode(size)


class Entity:
    def __init__(self, grid_x, grid_y, size_x, size_y):
        x = grid_x * size_x
        y = grid_y * size_x
        self.size_x = size_x
        self.size_y = size_y
        self.col = col["white"]

        # used for collision
        self.rect = pygame.Rect((x, y), (self.size_x, self.size_y))
        self.snap_to_grid()

    def get_grid_pos(self):
        grid_x = int(math.floor(self.rect.x / self.size_x))
        grid_y = int(math.floor(self.rect.y / self.size_y))
        return grid_x, grid_y

    def snap_to_grid(self):
        dx = math.floor(self.rect.centerx / block_size)
        dy = math.floor(self.rect.centery / block_size)
        self.rect = pygame.Rect((block_size * dx, block_size * dy), (self.size_x, self.size_y))


class SnakePart(Entity):

    def __init__(self, grid_x, grid_y, part_dir, head=False, tail=False):
        Entity.__init__(self, grid_x, grid_y, block_size, block_size)
        self.part_dir = part_dir
        self.head = head
        self.tail = False
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
        self.move_delay = 100
        self.time_since_move = 0

        #
        self.score = 0

        #
        self.growing = False

        self.snake_parts = [SnakePart(5, 5, 'left', head=True),
                            SnakePart(6, 5, 'left'),
                            SnakePart(7, 5, 'left'),
                            SnakePart(8, 5, 'left'),
                            SnakePart(9, 5, 'left'),
                            SnakePart(10, 5, 'left'),
                            SnakePart(11, 5, 'left'),
                            SnakePart(12, 5, 'left'),
                            SnakePart(13, 5, 'left'),
                            SnakePart(14, 5, 'left'),
                            SnakePart(15, 5, 'left', tail=True)]

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
        for i in range(len(self.snake_parts) - 1, 0, -1):
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

    def get_pos(self):
        blocked_pos = []
        for snake_part in self.snake_parts:
            blocked_pos.append((snake_part.get_grid_pos()))
        return blocked_pos

    def collision_self(self):
        snake_head = self.snake_parts[0]
        for snake_part in self.snake_parts[1:]:
            if snake_head.rect.colliderect(snake_part.rect):
                return False
        return True

    def collision_food(self, food):
        snake_head = self.snake_parts[0]
        if snake_head.rect.colliderect(food.rect):
            self.growing = True
            food.update_pos(get_valid_pos(self))

    def grow(self):
        self.snake_parts.append()


class Food(Entity):
    def __init__(self, valid_pos):
        grid_x, grid_y = random.choice(valid_pos)
        Entity.__init__(self, grid_x, grid_y, block_size, block_size)

    def draw(self):
        pygame.draw.circle(screen, self.col, self.rect.center, math.floor(block_size / 2))

    def update_pos(self, valid_pos):
        grid_x, grid_y = random.choice(valid_pos)
        x = grid_x * self.size_x
        y = grid_y * self.size_y
        self.rect = pygame.Rect((x, y), (self.size_x, self.size_y))
        self.snap_to_grid()

    def move(self, dt):
        pass


def draw_entities(snake, food):
    snake.draw()
    food.draw()


def draw_grid():
    for column in range(int(width / block_size + 1)):
        pygame.draw.line(screen, col["dark_grey"], (block_size * column, 0), (block_size * column, height), 1)
    for row in range(int(height / block_size + 1)):
        pygame.draw.line(screen, col["dark_grey"], (0, block_size * row), (width, block_size * row), 1)


def get_valid_pos(snake_obj):
    all_pos = [(i, j) for i in range(grid_size_x) for j in range(grid_size_y)]
    blocked_pos = snake_obj.get_pos()
    for pos in blocked_pos:
        all_pos.remove(pos)
    return all_pos


def game_loop():
    snake = Snake()
    grid_pos = get_valid_pos(snake)
    food = Food(grid_pos)
    dt = 0
    run = True
    while run:

        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

        # Move snake and get valid pos
        snake.move(dt)

        # Collision
        run = snake.collision_self()
        snake.collision_food(food)

        # Draw
        draw_grid()
        draw_entities(snake, food)
        pygame.display.update()

        # Update clock
        dt = clock.tick(30)
        print(clock.get_fps())

    print('game over')

if __name__ == '__main__':
    game_loop()
