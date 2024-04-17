
# a slightly hacked version of the game here:
#    https://drive.google.com/file/d/1gYrUMihRpdRP_9E_U7JQaLHyjiWlXFky/view

from z3 import *

import pygame
import random
import math

screen = pygame.display.set_mode([110, 500])
background_color = (255, 255, 255)  # RMB added RGB for white
clock = pygame.time.Clock()

class obstacle:
    def __init__(self, position, size):
        self.x,self.y = position
        self.size = size
        self.color = (200,0,0)

    def display(self):
        pygame.draw.circle(screen, self.color, (self.x,self.y), self.size, 0)

    def collision(self,player):
        dx = self.x - player.x
        dy = self.y - player.y
        dist = math.hypot(dx,dy)
        if dist < self.size + player.size:
            print("collided")
            return False
        else:
            return True

    def check_bounds(self):
        if self.x > 500 or self.y > 500:
            return False
        else:
            return True

    def move(self):
        self.y += 1

def decision(player,obstacle,S,count):
    x = Int('x')
    dx = player.x - obstacle.x
    dy = player.y - obstacle.y
    if dy < 6 and dy > 0:
        S.push()
        S.add(Or(dx + dy*x >= player.size + obstacle.size,dx + dy*x < -player.size - obstacle.size))
        return count + 1
    elif dy == 0 or dy == -1:
        S.push()
        S.add(Or(dx + x >= player.size + obstacle.size,dx + x <= -player.size - obstacle.size))
        return count + 1
    else:
        return count

obstacles = []

player = obstacle((55,485),2)   ## RMB 1 -> 2
player.color = (0,0,255)

S = Solver()
x = Int('x')
S.add(Or(x == 1,x == 0,x == -1))

pygame.display.set_caption("Dodge the Dots Z3")
pygame.init()
myfont = pygame.font.SysFont("monospace",13)

running = True
count = 0
decision_count = 0
move = 0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    ## screen.fill((0, 0, 0))
    screen.fill(background_color)  ## RMB added

    if (count - 499)%50 == 0 and count >= 499:
        for ob in obstacles:
            check = ob.check_bounds()
            if check == False:
                obstacles.remove(ob)

    for i in range(decision_count):
        S.pop()

    decision_count = 0

    for ob in obstacles:
        decision_count = decision(player,ob,S,decision_count)

    x = Int('x')
    S.push()
    S.add(player.x + x < 105)
    S.push()
    S.add(player.x + x > 5)
    decision_count += 2

    value = S.check()
    if value == unsat:
        print(S)
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False 

            for ob in obstacles:
                ob.display()

            player.display()

            label = myfont.render("Unsatisfiable",1,(255,255,255))
            screen.blit(label,(0,50))
            pygame.display.flip()
        break
        
    model = S.model()
    move = model[model[0]].as_long()

    player.display()

    for ob in obstacles:
        a = ob.collision(player)
        if not a:
            ob.color = (0,255,0)
        ob.display()
        ob.move()

    player.x = player.x + move

    if count%5 == 0:
        for i in range(int(random.random()*2)):
            x = random.randint(5,105)
            y = 0
            obstacles.append(obstacle((x,y),2))   ## RMB 1 -> 2

    count += 1
    # Flip the display
    pygame.display.flip()
    clock.tick(60)

# Done! Time to quit.
pygame.quit()
