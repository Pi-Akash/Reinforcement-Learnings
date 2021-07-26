# -*- coding: utf-8 -*-
"""
Created on Sun Jul 25 17:58:40 2021

@author: P Akash
"""

# importing libraries
import pygame
import random
from enum import Enum
from collections import namedtuple
import sys
import numpy as np

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

# snake game class controlled by AI
class SnakeGameAI():
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
        self.reset()
        
    
    def reset(self):
        """
        resets game state after every time the game ends
        """
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
        
        # initialize frame iteration variable
        # the variable helps break the game if the snake goes for a large time without collision or eating the food
        self.frame_iteration = 0
        
    def place_food(self):
        x = random.randint(0, (self.width - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (self.height - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.food = Point(x, y)
        
        if self.food in self.snake:
            self.place_food()
        
    def play_step(self, action):
        
        # incrementing frame_iteration value by 1, everytime play_step() gets called
        self.frame_iteration += 1
        
        # 1. will not collect user input as we want to control snake through AI
        for event in pygame.event.get():
            # pygame.QUIT is equal to when a person clicks on the close button 
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # 2. Snake movement
        # updating snake head based on the user input direction from above
        self.snake_move(action)
        self.snake.insert(0, self.head)
        
        # 3. check if game over
        # reward metric to improve our AI over time
        reward = 0
        game_over = False
        if self.is_collision() or self.frame_iteration > 100 * len(self.snake):
            game_over = True
            reward -= 10
            return reward, game_over, self.score
        
        # 4. check if snake has eaten the food
        # if eaten, place new food or else just move
        if self.head == self.food:
            self.score += 1
            reward += 10
            self.place_food()
        else:
            self.snake.pop()
        
        # 4. update UI and clock
        self.update_ui()
        self.clock.tick(SPEED)
        
        return reward, game_over, self.score
        
    
    def snake_move(self, action):
        
        # [straight, right, left], an of boolean values 
        # using which we want to define the next step
        
        # the snake can only take right or left turn at a time
        # list of all the possible Enum Direction values in clockwise direction
        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        
        # index of current direction value from clockwise list above
        current_direction_idx = clock_wise.index(self.direction)
        
        # go straight or no change
        if np.array_equal(action, [1,0,0]):
            new_direction = clock_wise[current_direction_idx]
        
        # action == right turn direction, r -> d -> l -> u
        elif np.array_equal(action, [0,1,0]):
            next_index = (current_direction_idx + 1) % 4
            new_direction = clock_wise[next_index]
            
        # action == left turn direction, r -> u -> l -> d
        else:
            next_index = (current_direction_idx - 1) % 4
            new_direction = clock_wise[next_index]
            
        self.direction = new_direction
        
        # current snake head position in the game window
        x = self.head.x
        y = self.head.y
        
        # update snake head coordinates based on input direction
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE
        
        # update the new head position based on above calculation
        self.head = Point(x, y)
        
    def is_collision(self, pt = None):
        
        # instead of using head, we are going to use a temp variable "pt" 
        # pt can take any coordinate value from snake body and can be used to decide collisions
        if pt is None:
            pt = self.head
        
        # hits boundary
        if pt.x > self.width - BLOCK_SIZE or pt.x < 0 or pt.y > self.height - BLOCK_SIZE or pt.y < 0:
            #print("-- Game over due to boundary collision")
            return True
        
        # hits itself
        if self.head in self.snake[1:]:
            #print("-- Game over due to self collision")
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
    

