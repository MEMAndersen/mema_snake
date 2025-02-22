import sys
import pygame
import random
import math
import copy

pygame.init()

# Init fonts
title_font = pygame.font.SysFont("comicsansms", 50)
under_title_font = pygame.font.SysFont("comicsansms", 20)

clock = pygame.time.Clock()

col = {
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "dark_grey": (25, 25, 25),
    "light_grey": (155, 155, 155),
}

size = width, height = 640, 480
block_size = 20
grid_size_x = int(width / block_size)
grid_size_y = int(height / block_size)

screen = pygame.display.set_mode(size)

state = "main_menu"


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
        self.draw_body()
        self.draw_eyes()

    def draw_body(self):
        pygame.draw.rect(screen, self.col, self.rect)

        lx = self.rect.x
        rx = lx + self.size_x
        ty = self.rect.y
        by = ty + self.size_y

        trim = int(block_size / 5)

        if self.part_dir == "up":
            for i in range(3):
                offset = trim * (i + 1)
                pygame.draw.line(screen, col["dark_grey"], (lx, ty + offset), (rx, ty + offset))
        elif self.part_dir == "left":
            for i in range(3):
                offset = trim * (i + 1)
                pygame.draw.line(screen, col["dark_grey"], (lx + offset, ty), (lx + offset, by))
        elif self.part_dir == "down":
            for i in range(3):
                offset = trim * (i + 1)
                pygame.draw.line(screen, col["dark_grey"], (rx, by - offset), (lx, by - offset))
        elif self.part_dir == "right":
            for i in range(3):
                offset = trim * (i + 1)
                pygame.draw.line(screen, col["dark_grey"], (rx - offset, by), (rx - offset, ty))

    def draw_eyes(self):
        cx = self.rect.centerx
        cy = self.rect.centery
        offset = int(block_size / 5)

        if self.head is True:
            if self.part_dir == "up":
                pos1 = (cx - offset, cy - offset)
                pos2 = (cx + offset, cy - offset)
            elif self.part_dir == "left":
                pos1 = (cx - offset, cy - offset)
                pos2 = (cx - offset, cy + offset)
            elif self.part_dir == "down":
                pos1 = (cx + offset, cy + offset)
                pos2 = (cx - offset, cy + offset)
            elif self.part_dir == "right":
                pos1 = (cx + offset, cy + offset)
                pos2 = (cx + offset, cy - offset)

            pygame.draw.circle(screen, col["dark_grey"], pos1, 1)
            pygame.draw.circle(screen, col["dark_grey"], pos2, 1)

    def move(self):
        if self.part_dir == "up":
            self.rect = self.rect.move(0, -block_size)
        elif self.part_dir == "left":
            self.rect = self.rect.move(-block_size, 0)
        elif self.part_dir == "down":
            self.rect = self.rect.move(0, block_size)
        elif self.part_dir == "right":
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
        self.level_decrement = 10

        #
        self.level = 1
        self.score = 0
        self.food_eaten = 0

        #
        self.growing = False

        self.snake_parts = [
            SnakePart(5, 5, "left", head=True),
            SnakePart(6, 5, "left", tail=True),
        ]

    def draw(self):
        for snake_part in self.snake_parts:
            snake_part.draw()

    def update_snake_head_dir(self, key: int):
        # Change direction of snake head by user input
        if key == pygame.K_UP and self.snake_parts[0].previous_dir != "down":
            self.snake_parts[0].part_dir = "up"
        elif key == pygame.K_LEFT and self.snake_parts[0].previous_dir != "right":
            self.snake_parts[0].part_dir = "left"
        elif key == pygame.K_DOWN and self.snake_parts[0].previous_dir != "up":
            self.snake_parts[0].part_dir = "down"
        elif key == pygame.K_RIGHT and self.snake_parts[0].previous_dir != "left":
            self.snake_parts[0].part_dir = "right"

    def update_snake_body_dir(self):
        for i in range(len(self.snake_parts) - 1, 0, -1):
            self.snake_parts[i].part_dir = self.snake_parts[i - 1].part_dir

    def move(self, dt) -> bool:
        "Returns true if moved, otherwise false"

        self.time_since_move += dt
        if self.time_since_move >= self.move_delay:
            # Get last snake_part to use if growing
            new_tail = copy.copy(self.snake_parts[-1])

            # resetting time delay and moves
            self.time_since_move -= self.move_delay

            for snake_part in self.snake_parts:
                snake_part.move()

            if self.growing:
                self.snake_parts.append(new_tail)
                self.growing = False

            self.update_snake_body_dir()
            return True
        return False

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
            self.score += self.level
            self.food_eaten += 1

        if self.food_eaten % 10 == 0 and self.level != 9 and self.food_eaten != 0:
            self.level += 1
            self.food_eaten = 0
            self.move_delay -= self.level_decrement

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
        pygame.draw.line(
            screen,
            col["dark_grey"],
            (block_size * column, 0),
            (block_size * column, height),
            1,
        )
    for row in range(int(height / block_size + 1)):
        pygame.draw.line(
            screen,
            col["dark_grey"],
            (0, block_size * row),
            (width, block_size * row),
            1,
        )


def get_valid_pos(snake_obj):
    all_pos = [(i, j) for i in range(grid_size_x) for j in range(grid_size_y)]
    blocked_pos = snake_obj.get_pos()
    for pos in blocked_pos:
        all_pos.remove(pos)
    return all_pos


def print_fps():
    pass


def render_blit_text(font_obj, text, center_x, center_y):
    text_size = font_obj.size(text)
    text_render = font_obj.render(text, True, col["light_grey"])
    screen.blit(text_render, [center_x - text_size[0] / 2, center_y - text_size[1] / 2])


def print_game_over_screen(level, score):
    render_blit_text(title_font, "GAME OVER", width / 2, int(height / 3))
    render_blit_text(title_font, "Level reached: " + str(level), width / 2, int(height / 3 + 50))
    render_blit_text(title_font, "Score: " + str(score), width / 2, int(height / 3 + 100))
    render_blit_text(
        under_title_font, "Press any key to return to main menu", width / 2, int(height / 3 + 140)
    )
    pygame.display.update()


def main_menu_loop():
    main_menu = True
    while main_menu:
        screen.fill((0, 0, 0))
        pygame.display.set_caption("Snake")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                return "game"

        # Write text to main menu.
        render_blit_text(title_font, "Snake", width / 2, int(height / 3))
        render_blit_text(
            under_title_font, "by Mads Emil Møller Andersen (MEMA)", width / 2, int(height / 3) + 40
        )
        render_blit_text(
            under_title_font, "Control the snake using the arrowkeys", width / 2, int(height / 2) + 40
        )
        render_blit_text(
            under_title_font, "Press any button to start the game", width / 2, int(height / 2) + 60
        )

        # draw_grid()
        pygame.display.update()


def game_loop():
    snake = Snake()
    grid_pos = get_valid_pos(snake)
    food = Food(grid_pos)
    dt = 0
    run = True

    while run:
        screen.fill((0, 0, 0))
        pygame.display.set_caption("score: " + str(int(snake.score)) + "  level: " + str(int(snake.level)))

        # Handle input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.KEYDOWN:
                snake.update_snake_head_dir(event.key)
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
        dt = clock.tick(60)

    print_game_over_screen(snake.level, snake.score)
    pygame.time.delay(5000)
    pygame.event.clear(pygame.KEYDOWN)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                return "main_menu"


if __name__ == "__main__":
    while True:
        if state == "main_menu":
            state = main_menu_loop()
        elif state == "game":
            state = game_loop()
        else:
            break
