#imports
import neat
from neat import genome
import pygame
import UI
import time
import ENV
import os
import math
import matplotlib.pyplot as plt

scores = []
gen = []
gener = 0

def main(genomes, config):
    pygame.init()
    screen = pygame.display.set_mode((800,600))
    pygame.display.set_caption("Tetris!")
    ui = UI.UI(screen, genomes, config)
    env = ENV.ENV(ui)


    running = True
    clock = pygame.time.Clock()

    while running:
        clock.tick(60)

        eventList = pygame.event.get()

        pipe_ind = 0
        if len(ui.birds) > 0:
            if len(ui.pipes) > 1 and ui.birds[0].x > ui.pipes[0].x + ui.pipes[0].topImg.get_width():
                pipe_ind = 1
        
        ui.move()
        for x, bird in enumerate(ui.birds):
            bird.move()
            ui.ge[x].fitness += 0.1

            topDist = math.sqrt((bird.y - ui.pipes[pipe_ind].height)**2 + (bird.x - ui.pipes[pipe_ind].x)**2)
            botDist = math.sqrt((bird.y - ui.pipes[pipe_ind].bottom)**2 + (bird.x - ui.pipes[pipe_ind].x)**2)
            topDist2 = math.sqrt((bird.y - ui.pipes[pipe_ind].height)**2 + (bird.x - (ui.pipes[pipe_ind].x + ui.pipes[pipe_ind].topImg.get_width()))**2)
            botDist2 = math.sqrt((bird.y - ui.pipes[pipe_ind].bottom)**2 + (bird.x - (ui.pipes[pipe_ind].x + ui.pipes[pipe_ind].topImg.get_width()))**2)
            #print(topDist2)
            #output = ui.nets[x].activate((bird.y, abs(bird.y - ui.pipes[pipe_ind].height), abs(bird.y - ui.pipes[pipe_ind].bottom)))
            
            output = ui.nets[x].activate((bird.y, topDist, botDist))

            if output[0] > 0.5:
                bird.jump()


        for event in eventList:
            if event.type == pygame.QUIT:
                running = False
            # if event.type == pygame.KEYDOWN:
            #     if event.key == pygame.K_SPACE:
            #         ui.birds[0].jump()
            #     if event.key == pygame.K_b and len(ui.birds) == 2:
            #         ui.birds[1].jump()
        
        global gener
        global gen
        global scores
        if len(ui.birds) == 0:
            gener += 1
            gen.append(gener)
            scores.append(ui.fscore)
            running = False

        #ui.move()
        ui.update()
        pygame.display.update()

#main()
def run(conPath):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, conPath)
    pop = neat.Population(config)
    pop.add_reporter(neat.StdOutReporter(True))
    pop.add_reporter(neat.StatisticsReporter())

    winner = pop.run(main, 10)
    print(winner)
    plt.plot(gen, scores)
    plt.show()


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    conPath = os.path.join(local_dir, "config-feedforward.txt")
    run(conPath)
    #main(1, 2)