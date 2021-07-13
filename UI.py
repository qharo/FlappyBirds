from neat import genome
import pygame
import os
import random
import neat

pygame.font.init()

COLORS = [
    (255, 255, 255), #WHITE
    (0,0,0), #BLACK
    (255, 255, 240), #CREAM
    (255, 0, 0), #RED
    (136, 140, 141), #STONE
]

# BIRD CLASS
class Bird:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel = 0
        self.tick = 0
        self.img = pygame.image.load(os.path.join("images", "bird1.png"))

    def jump(self):
        self.vel = -7
        self.tick = 0
    
    def move(self):
        self.tick += 1
        
        d = self.tick*self.vel + 1*(self.tick**2)
        if d >= 16:
            d = 16
        else:
            d -= 2

        self.y += d
    
    def draw(self, screen):
        screen.blit(self.img, (self.x, self.y))
    
    def get_mask(self):
        return pygame.mask.from_surface(self.img)



class Pipe:    
    def __init__(self, x):
        self.x = x
        self.botImg = pygame.image.load(os.path.join("images", "pipe.png"))
        self.topImg = pygame.transform.flip(pygame.image.load(os.path.join("images", "pipe.png")), False, True)
        self.passed = False
        self.vel = 5
        self.gap = random.randrange(110, 160)
        self.imgHeight = self.topImg.get_height()
        self.setHeight()

    def setHeight(self):
        self.height = random.randrange(180 - self.gap, 320) #180 is the length of the lower img, need 
        self.top = self.height - self.topImg.get_height()
        self.bottom = self.height + self.gap

    def move(self): #MOVES THEM LEFTWARD
        self.x -= self.vel
    
    def draw(self, screen):
        screen.blit(self.topImg, (self.x, self.top))
        screen.blit(self.botImg, (self.x, self.bottom))

    def collide(self, bird):
        birdMask = bird.get_mask()
        topMask = pygame.mask.from_surface(self.topImg)
        botMask = pygame.mask.from_surface(self.botImg)

        topOffset = (self.x - bird.x, self.top - round(bird.y))
        botOffset = (self.x - bird.x, self.bottom - round(bird.y))

        bPoint = birdMask.overlap(botMask, botOffset)
        tPoint = birdMask.overlap(topMask, topOffset)

        if tPoint or bPoint:
            return True
        return False


class Base:
    def __init__(self, y):
        self.vel = 5
        self.img = pygame.image.load(os.path.join("images", "base.png"))
        self.width = self.img.get_width()
        self.y = y
        self.x1 = 0
        self.x2 = self.width
        self.x3 = self.x2 + self.width

    def move(self):
        self.x1 -= self.vel
        self.x2 -= self.vel
        self.x3 -= self.vel
        
        if self.x1 + self.width < 0:
            self.x1 = self.x3 + self.width        
        
        if self.x2 + self.width < 0:
            self.x2 = self.x1 + self.width      
        
        if self.x3 + self.width < 0:
            self.x3 = self.x2 + self.width
    
    def draw(self, screen):
        screen.blit(self.img, (self.x1, self.y))
        screen.blit(self.img, (self.x2, self.y))
        screen.blit(self.img, (self.x3, self.y))




class UI:
    def rect(self, color, pos):
        pygame.draw.rect(self.screen, color, pos)

    def __init__(self, screen, genomes, config):
        self.screen = screen
        self.nets = []
        self.ge = []
        self.birds = []

        for genome_id, genome in genomes:
            net = neat.nn.FeedForwardNetwork.create(genome, config)
            self.nets.append(net)
            self.birds.append(Bird(230, 350))
            genome.fitness = 0
            self.ge.append(genome)

        #self.birds = [Bird(230, 50), Bird(210, 50)]
        #print(self.birds)

        
        self.pipes = [Pipe(500)]
        self.base = Base(500)
        self.font = pygame.font.SysFont("comicsans", 30)
        #self.collided = False
        self.fscore = 0
        self.steps = 0
    
    def move(self):
        addPipe = False
        removePipe = False
        for pipe in self.pipes:
            for x, bird in enumerate(self.birds):
                #CHECKS IF BIRD COLLIDES WITH PIPE
                if pipe.collide(bird):
                    #self.collided = True
                    self.ge[x].fitness -= -1
                    self.birds.pop(x)
                    self.nets.pop(x)
                    self.ge.pop(x)

                # ELSE, IF THE BIRDS PASS A PIPE, ADD A NEW PIPE
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    addPipe = True
                    self.fscore += 20


            if pipe.x + pipe.topImg.get_width() < 0:
                self.rem = pipe
                removePipe = True
            
            pipe.move()
        
        if addPipe:
            self.pipes.append(Pipe(500))
            addPipe = False
            for g in self.ge:
                g.fitness += 5
        
        if removePipe:
            self.pipes.remove(self.rem)
            removePipe = False

        for x, bird in enumerate(self.birds):
            if bird.y > 500 or bird.y < 0:
                self.birds.pop(x)
                self.nets.pop(x)
                self.ge.pop(x)
            #bird.move()
        self.base.move()

    def update(self):
        self.steps += 1
        self.rect(COLORS[1], [0,0,500,600])
        for x, bird in enumerate(self.birds):
            #print(self.birds[x])
            self.birds[x].draw(self.screen)
        for pipe in self.pipes:
            pipe.draw(self.screen)
        self.base.draw(self.screen)

        text = self.font.render(f"Score: {self.fscore + self.steps//10}", 1, (255, 255, 255))
        self.screen.blit(text, (380, 10))

        self.rect(COLORS[2], [500, 0, 300, 600])