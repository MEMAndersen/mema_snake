import sys
import pygame
import random
import numpy as np

pygame.init()

clock = pygame.time.Clock()

size = width, height = 640, 480
entities = np.array([])
run = True
directions = ('up', 'left', 'down', 'right')

screen = pygame.display.set_mode(size)


class Entity:
    def __init__(self, x, y, size_x, size_y):
        self.x = x
        self.y = y
        self.size_x = size_x
        self.size_y = size_y
        self.col = (255, 255, 255)
        self.speed = 0
        self.dir = random.choice(directions)
        # used for collision
        self.rect = pygame.Rect((self.x, self.y), (self.size_x, self.size_y))
        self.length = 1

    def draw(self):
        if self.x < self.size_x/2
        pygame.draw.rect(screen, self.col, self.rect)

    def move(self, dt):

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.dir = 'up'
        if keys[pygame.K_LEFT]:
            self.dir = 'left'
        if keys[pygame.K_DOWN]:
            self.dir = 'down'
        if keys[pygame.K_RIGHT]:
            self.dir = 'right'

        if self.dir == 'up':
            self.y -= self.speed * dt / 1000
        elif self.dir == 'left':
            self.x -= self.speed * dt / 1000
        elif self.dir == 'down':
            self.y += self.speed * dt / 1000
        elif self.dir == 'right':
            self.x += self.speed * dt / 1000

        self.edges()

        self.rect = pygame.Rect((self.x, self.y), (self.size_x, self.size_y))

    def edges(self):
        if self.x < 0:
            self.x += width
        elif self.x > width:
            self.x -= width

        if self.y < 0:
            self.y += height
        elif self.y > height:
            self.y -= height


class Snake(Entity):
    def __init__(self, x, y):
        Entity.__init__(self, x, y, 20, 20)
        self.speed = 50
        self.food = 0

    def collision(self):
        for entity in entities[entities != self]:
            if self.rect.colliderect(entity.rect):
                self.food += 1


class Food(Entity):
    def __init__(self, x, y):
        Entity.__init__(self, x, y, 10, 10)


def draw_entities():
    for entity in entities:
        entity.draw()


def move_entities(dt):
    for entity in entities:
        if entity.speed != 0:
            entity.move(dt)


def edges():
    for entity in entities:
        if entity.speed != 0:
            pass


def game_loop():
    while run:

        dt = clock.tick(60)
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

        move_entities(dt)
        draw_entities()
        pygame.display.update()


if __name__ == '__main__':
    print('here')
    entities = np.append(entities, Snake(50, 50))
    entities = np.append(entities, (Food(random.randint(0, width), random.randint(0, height))))
    print(entities)
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
