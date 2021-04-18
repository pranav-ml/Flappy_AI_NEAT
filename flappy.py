import neat
import pygame
import random
import os

pygame.init()
win_width = 500
win_height = 700

birdimg = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),
           pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),
           pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]
pipeimg = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
baseimg = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
bgimg = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

win = pygame.display.set_mode((win_width, win_height))
sfont = pygame.font.SysFont("comicsans", 50, True)
gen = 0


class Bird:
    max_rotation = 25
    animation = 5
    rot_vel = 20

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.vel = 0
        self.tick_count = 0
        self.img = birdimg[0]
        self.img_count = 0
        self.d = 0

    def jump(self):
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1
        self.d = self.vel * self.tick_count + 1.5 * self.tick_count ** 2
        if self.d >= 16:
            self.d = 16
        self.y += self.d
        if self.d < 0:
            self.tilt = self.max_rotation
        else:
            if self.tilt > -90:
                self.tilt -= self.rot_vel
            else:
                self.tilt = -90

    def draw(self):
        if self.img_count >= 12:
            self.img_count = 0
        if self.d < 0:
            self.img = birdimg[self.img_count // 6]
        else:
            self.img = birdimg[1]
        rotated_img = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_img.get_rect(center=self.img.get_rect(topleft=(int(self.x), int(self.y))).center)
        win.blit(rotated_img, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Base:
    VEL = 5
    WIDTH = baseimg.get_width()
    IMG = baseimg

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


class Pipe():
    def __init__(self, x):
        self.x = x
        self.vel = 5
        self.gap = 200
        self.height = 0
        self.ptop = pygame.transform.flip(pipeimg, False, True)
        self.pbottom = pipeimg
        self.top = 0
        self.bottom = 0
        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 430)
        self.top = self.height - self.ptop.get_height()
        self.bottom = self.height + self.gap

    def move(self):
        self.x -= self.vel

    def draw(self):
        win.blit(self.ptop, (self.x, self.top))
        win.blit(self.pbottom, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.ptop)
        bottom_mask = pygame.mask.from_surface(self.pbottom)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)
        if b_point or t_point:
            return True
        else:
            return False


def redrawWin(pipes, birds, base):
    win.blit(bgimg, (0, -100))
    base.draw()
    for pipe in pipes:
        pipe.draw()
    for bird in birds:
        bird.draw()
    text = sfont.render("Score:" + str(score), 1, (255, 255, 255))
    win.blit(text, (20, 20))
    text = sfont.render("Gen:" + str(gen), 1, (255, 255, 255))
    win.blit(text, (350, 20))
    text = sfont.render("Alive:" + str(len(birds)), 1, (255, 255, 255))
    win.blit(text, (20, 60))
    pygame.display.update()


def main(genomes, config):
    space = 0
    clock = pygame.time.Clock()
    global score
    score = 0
    global gen
    gen += 1
    base = Base(630)
    pipes = [Pipe(700)]
    run = True
    birds = []
    nets = []
    ge = []
    for l, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(100, 200))
        g.fitness = 0
        ge.append(g)

    while run:
        clock.tick(30)

        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 0 and birds[0].x > pipes[0].x + pipes[0].ptop.get_width():
                pipe_ind = 1
        else:
            break
        for x, bird in enumerate(birds):
            bird.move()
            bird.img_count += 1
            ge[x].fitness += 0.1
            output = nets[x].activate(
                (bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))
            if output[0] <0.5:
                bird.jump()
            else:
                pass
        base.move()
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 5
                    birds.remove(bird)
                    nets.pop(x)
                    ge.pop(x)

            pipe.move()

            if pipe.x == 0:
                pipes.append(Pipe(500))
                score += 1
                for g in ge:
                    g.fitness += 10
            if pipe.x + pipe.ptop.get_width() < 0:
                pipes.remove(pipe)
        for x, bird in enumerate(birds):
            if bird.y >= 560 or bird.y < 0:

                birds.remove(bird)
                nets.pop(x)
                ge.pop(x)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                exit()

        redrawWin(pipes, birds, base)


def run(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)
    p = neat.Population(config)



    p.run(main, 100)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)
