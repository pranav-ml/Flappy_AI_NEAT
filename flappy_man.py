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


    def move(self):
        self.tick_count += 1
        self.d = self.vel * self.tick_count + 1.5 * self.tick_count ** 2
        if self.d >= 16:
            self.d = 16
        if self.y < 0:
            self.y=1
        self.y += self.d

        if self.d < 0:
            self.tilt = self.max_rotation
        else:
            if self.tilt > -90:
                self.tilt -= self.rot_vel
            else:
                self.tilt = -90

    def draw(self):
        self.img_count+=1
        if self.img_count >= 12:
            self.img_count = 0
        if self.d < 0:
            self.img = birdimg[self.img_count // 6]
        else:
            self.img = birdimg[1]
        rotated_img = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_img.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
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


def redrawWin(pipes, bird, base):
    win.blit(bgimg, (0, -100))
    bird.draw()
    base.draw()
    for pipe in pipes:
        pipe.draw()
    text = sfont.render("Score:" + str(score), 1, (255, 255, 255))
    win.blit(text, (20, 20))
    pygame.display.update()

def main():
    space = 0
    clock = pygame.time.Clock()
    global score
    score = 0
    global gen
    base = Base(630)
    pipes = [Pipe(700)]
    run = True
    bird=Bird(100,200)
    gd=1
    while run:

        if gd == 1:
            clock.tick(30)

            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE ]:
                if space==0:
                    bird.jump()
                    space=1
            else:
                space=0
            bird.move()

            base.move()
            for pipe in pipes:
                if pipe.collide(bird):

                    gd=0
                pipe.move()
                if pipe.x == 0:
                    pipes.append(Pipe(500))
                    score += 1
                if pipe.x + pipe.ptop.get_width() < 0:
                    pipes.remove(pipe)
            if bird.y>=570:

                gd=0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    pygame.quit()
            redrawWin(pipes, bird, base)
        else:
            win.blit(bgimg, (0, -100))
            text2 = sfont.render("GAME OVER", 1, (255, 255, 255))
            text3 = sfont.render("YOUR SCORE:" + str(score), 1, (255, 255, 255))
            file = open("highscore.txt", "r")
            high = file.read()
            highscore = int(high)
            file.close()
            if score>highscore:
                file2=open("highscore.txt","w")
                file2.write(str(score))
                file2.close()
                highscore=score
            text4 = sfont.render("HI-SCORE:" + str(highscore), 1, (255,0,0))
            win.blit(text2, (130, 220))
            win.blit(text3, (100, 320))
            win.blit(text4, (130, 420))
            pygame.display.update()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RIGHT]:
                main()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    pygame.quit()
                    quit()

main()


