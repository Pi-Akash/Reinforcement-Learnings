# -*- coding: utf-8 -*-
"""
Created on Sat Jul 24 16:14:24 2021

@author: P Akash
"""

# importing libraries
import pygame
import random
from enum import Enum
from collections import namedtuple
import sys

# initializing pygame modules
pygame.init()

# initialize game font
font = pygame.font.Font('arial.ttf', 25)

# lightweight namedtuple object can be accessible through name or indices
Point = namedtuple("Point", ["x", "y"])

# a block size for coordinate reference in game window
BLOCK_SIZE = 20

# clock framerate parameters, fps rate
SPEED = 10

# RGB colors
WHITE = (255, 255, 255)
RED = (200, 0, 0)
BLUE1 = (0, 0, 255) # color for outer square of snake body
BLUE2 = (0, 100, 255) # color for inner square of snake body 
BLACK = (0, 0, 0)

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

class SnakeGame():
    def __init__(self, window_width = 640, window_height = 480):
        
        # initialization of game window properties
        self.width = window_width
        self.height = window_height
        
        # initialize game window
        # pygame.display.set_mode(size = (width, height)) : Initialize a window or screen for display
        self.display = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Snake Game")
        
        # pygame.time.Clock() : create an object to help track time.
        self.clock = pygame.time.Clock()
        
        # intial game state
        # snake direction
        self.direction = Direction.RIGHT
        
        # snake head at the middle of the game window
        self.head = Point(self.width//2, self.height//2)
        
        # snake body
        # we are going to initial snake of only 2 BLOCK_SIZE
        self.snake = [self.head, Point(self.head.x - BLOCK_SIZE, self.head.y)]
        
        # initialize score
        self.score = 0
        
        # initialize food and place in game window
        self.food = None
        self.place_food()
        
    def place_food(self):
        x = random.randint(0, (self.width - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (self.height - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.food = Point(x, y)
        
        if self.food in self.snake:
            self.place_food()
        
    def play_step(self):
        # 1. Collect user input
        for event in pygame.event.get():
            # pygame.QUIT is equal to when a person clicks on the close button 
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # pygame.KEYDOWN is to check is any key is pressed down
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.direction = Direction.LEFT
                elif event.key == pygame.K_RIGHT:
                    self.direction = Direction.RIGHT
                elif event.key == pygame.K_UP:
                    self.direction = Direction.UP
                elif event.key == pygame.K_DOWN:
                    self.direction = Direction.DOWN
        
        # 2. Snake movement
        # updating snake head based on the user input direction from above
        self.snake_move(self.direction)
        self.snake.insert(0, self.head)
        
        # 3. check if game over
        game_over = False
        if self._is_collision():
            game_over = True
            return game_over, self.score
        
        # 4. check if snake has eaten the food
        # if eaten, place new food or else just move
        if self.head == self.food:
            self.score += 1
            self.place_food()
        else:
            self.snake.pop()
        
        # 4. update UI and clock
        self.update_ui()
        self.clock.tick(SPEED)
        
        return game_over, self.score
        
    
    def snake_move(self, direction):
        # current snake head position in the game window
        x = self.head.x
        y = self.head.y
        
        # update snake head coordinates based on input direction
        if direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif direction == Direction.UP:
            y -= BLOCK_SIZE
        
        # update the new head position based on above calculation
        self.head = Point(x, y)
        
    def _is_collision(self):
        # hits boundary
        if self.head.x > self.width - BLOCK_SIZE or self.head.x < 0 or self.head.y > self.height - BLOCK_SIZE or self.head.y < 0:
            print("-- Game over due to boundary collision")
            return True
        
        # hits itself
        if self.head in self.snake[1:]:
            print("-- Game over due to self collision")
            return True
        
        return False
            
    def update_ui(self):
        # fill the game display with black color
        self.display.fill(BLACK)
        
        # draws snake on screen
        for pt in self.snake:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x + 4, pt.y + 4, 12, 12))
        
        # draws food on the screen
        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))
        
        # writing score on screen
        # font.render(text, antialias, color, background = None)
        # antialias is a boolean argumant, if true the character will have smooth edges
        text = font.render("Score: " + str(self.score), True, WHITE)
        
        # blit or overlap the surface on the canvas at the given position
        # for more information on blit, please go through the below link:
        # https://stackoverflow.com/questions/37800894/what-is-the-surface-blit-function-in-pygame-what-does-it-do-how-does-it-work
        # Inshort we are trying to draw whatever is there in text object in the (0,0) position
        self.display.blit(text, [0,0])
        
        # updates the components of the entire display
        pygame.display.flip()
        
        
if __name__ == "__main__":
    
    # SnakeGame class object
    game = SnakeGame()
    
    while True:
        game_over, score = game.play_step()
        
        if game_over == True:
            break
        
    print("Current score : ", score)
    pygame.quit()
    
