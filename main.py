# Modules
import neat
import pygame
import os
import random
import math
import sys

pygame.init()

# Global vars
curr_best_fitness = 0
last_fitness = []

# Game window vars
WINDOW_HEIGHT = 600
WINDOW_WIDTH = 1100
GAME_WINDOW = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

# Dino Images
RUNNING_IMGS = [pygame.image.load(os.path.join('Images/Dino', 'DinoRun1.png')),
                pygame.image.load(os.path.join('Images/Dino', 'DinoRun2.png'))]

JUMPING_IMG = pygame.image.load(os.path.join('Images/Dino', 'DinoJump.png'))

# Obstacle Images (Cacti)
SMALL_CACTUS_IMGS = [pygame.image.load(os.path.join('Images/Cactus', 'SmallCactus1.png')),
                     pygame.image.load(os.path.join('Images/Cactus', 'SmallCactus2.png')),
                     pygame.image.load(os.path.join('Images/Cactus', 'SmallCactus3.png'))]

LARGE_CACTUS_IMGS = [pygame.image.load(os.path.join('Images/Cactus', 'LargeCactus1.png')),
                     pygame.image.load(os.path.join('Images/Cactus', 'LargeCactus2.png')),
                     pygame.image.load(os.path.join('Images/Cactus', 'LargeCactus3.png')), ]

# Background
BACKGROUND = pygame.image.load(os.path.join('Images/Other', 'Track.png'))

# Font
FONT = pygame.font.Font('freesansbold.ttf', 20)


class Dino:
    X_POS = 80
    Y_POS = 310

    # Jump velocity
    VELOCITY = 8.5

    def __init__(self, img=RUNNING_IMGS[0]):
        self.image = img
        self.dino_run = True
        self.dino_jump = False
        self.velocity = self.VELOCITY
        self.rect = pygame.Rect(self.X_POS, self.Y_POS, img.get_width(), img.get_height())
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.step_count = 0

    # Updates the dino image depending on what it is doing
    def update(self):
        if self.dino_run:
            self.run_step()
        if self.dino_jump:
            self.jump()
        if self.step_count >= 10:
            self.step_count = 0

    # Controls the jumping of the dino
    def jump(self):
        self.image = JUMPING_IMG
        if self.dino_jump:
            self.rect.y -= self.velocity * 4
            self.velocity -= 0.8
        if self.velocity <= -self.VELOCITY:
            self.dino_jump = False
            self.dino_run = True
            self.velocity = self.VELOCITY

    def run_step(self):
        self.image = RUNNING_IMGS[self.step_count // 5]
        self.rect.x = self.X_POS
        self.rect.y = self.Y_POS
        self.step_count += 1

    def draw(self, window):
        window.blit(self.image, (self.rect.x, self.rect.y))
        pygame.draw.rect(window, self.color, (self.rect.x, self.rect.y, self.rect.width, self.rect.height), 2)

        for obstacle in obstacles:
            pygame.draw.line(window, self.color, (self.rect.x + 54, self.rect.y + 12), obstacle.rect.center, 2)


class Obstacle:
    def __init__(self, image, number_of_cacti):
        self.image = image
        self.type = number_of_cacti
        self.rect = self.image[self.type].get_rect()
        self.rect.x = WINDOW_WIDTH
        self.color = (255, 0, 0)

    def update(self):
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            obstacles.pop()

    def draw(self, window):
        window.blit(self.image[self.type], self.rect)
        pygame.draw.rect(window, self.color, (self.rect.x, self.rect.y, self.rect.width, self.rect.height), 2)


class SmallCactus(Obstacle):
    def __init__(self, image, number_of_cacti):
        super().__init__(image, number_of_cacti)
        self.rect.y = 325


class LargeCactus(Obstacle):
    def __init__(self, image, number_of_cacti):
        super().__init__(image, number_of_cacti)
        self.rect.y = 300


def remove(index):
    ge.pop(index)
    nets.pop(index)
    dinos.pop(index)


def distance(pos_a, pos_b):
    dx = pos_a[0] - pos_b[0]
    dy = pos_a[1] - pos_b[1]
    return math.sqrt(dx ** 2 + dy ** 2)


def eval_genomes(genomes, config):
    global game_speed, x_pos_background, y_pos_background, obstacles, dinos, ge, nets, points, last_fitness, curr_best_fitness
    clock = pygame.time.Clock()
    points = 0

    obstacles = []
    dinos = []
    ge = []
    nets = []
    dead_dinos = []
    curr_best_fitness = 0

    x_pos_background = 0
    y_pos_background = 380
    game_speed = 20

    for genome_id, genome in genomes:
        dinos.append(Dino())
        ge.append(genome)
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0

    def score():
        global points, game_speed
        points += 1
        if points % 100 == 0:
            game_speed += 1
        text = FONT.render(f'Points:  {str(points)}', True, (0, 0, 0))
        GAME_WINDOW.blit(text, (950, 50))

    def statistics():
        global dinos, game_speed, ge
        text_1 = FONT.render(f'Dinosaurs Alive:  {str(len(dinos))}', True, (0, 0, 0))
        text_2 = FONT.render(f'Generation:  {pop.generation + 1}', True, (0, 0, 0))
        text_3 = FONT.render(f'Game Speed:  {str(game_speed)}', True, (0, 0, 0))
        text_4 = FONT.render(f'Best Performance Over Time:  {str(last_fitness)}', True, (0, 0, 0))

        GAME_WINDOW.blit(text_1, (50, 450))
        GAME_WINDOW.blit(text_2, (50, 480))
        GAME_WINDOW.blit(text_3, (50, 510))
        GAME_WINDOW.blit(text_4, (50, 540))

    def background():
        global x_pos_background, y_pos_background
        image_width = BACKGROUND.get_width()
        GAME_WINDOW.blit(BACKGROUND, (x_pos_background, y_pos_background))
        GAME_WINDOW.blit(BACKGROUND, (image_width + x_pos_background, y_pos_background))

        if x_pos_background <= -image_width:
            x_pos_background = 0

        x_pos_background -= game_speed

    run = True

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        GAME_WINDOW.fill((255, 255, 255))

        for dino in dinos:
            dino.update()
            dino.draw(GAME_WINDOW)

        if len(dinos) == 0:
            last_fitness.append(curr_best_fitness)
            break

        if len(obstacles) == 0:
            rand_int = random.randint(0, 1)
            if rand_int == 0:
                obstacles.append(SmallCactus(SMALL_CACTUS_IMGS, random.randint(0, 2)))
            elif rand_int == 1:
                obstacles.append(LargeCactus(LARGE_CACTUS_IMGS, random.randint(0, 2)))

        for obstacle in obstacles:
            obstacle.draw(GAME_WINDOW)
            obstacle.update()
            for i, dino in enumerate(dinos):
                if dino.rect.colliderect(obstacle.rect):
                    ge[i].fitness -= 1

                    if ge[i].fitness > curr_best_fitness:
                        curr_best_fitness = ge[i].fitness

                    dead_dinos.append(dino)
                    remove(i)
                else:
                    ge[i].fitness += 1

        for i, dino in enumerate(dinos):
            output = nets[i].activate((dino.rect.y,
                                       distance((dino.rect.x, dino.rect.y),
                                                obstacle.rect.midtop)))

            if output[0] > 0.5 and dino.rect.y == dino.Y_POS:
                dino.dino_jump = True
                dino.dino_run = False

        statistics()
        score()
        background()
        clock.tick(30)
        pygame.display.update()


# NEAT Neural Net Setup
def run(config_path):
    global pop
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    pop = neat.Population(config)
    pop.run(eval_genomes, 50)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    con_path = os.path.join(local_dir, 'config.txt')
    run(con_path)
