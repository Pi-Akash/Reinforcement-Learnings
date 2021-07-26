# -*- coding: utf-8 -*-
"""
Created on Sun Jul 25 18:57:46 2021

@author: P Akash
"""

# importing libraries
import torch
import random
import numpy as np
from collections import deque
from snake_pygame_ai import SnakeGameAI 
from snake_pygame_ai import Direction 
from snake_pygame_ai import Point
from model_snake_pygame import Linear_QNet, QTrainer
from helper_snake_pygame import plot


MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LEARNING_RATE = 0.001
# a block size for coordinate reference in game window
BLOCK_SIZE = 20

class Agent():
    def __init__(self):
        self.number_of_games = 0
        self.epsilon = 0 # randomness parameter
        self.gamma = 0.9 # discount rate, must be smaller than 1
        self.memory = deque(maxlen = MAX_MEMORY) # popleft() if memory greater than MAX_MEMORY
        
        # model parameters
        self.input_size = 11
        self.hidden_size = 256
        self.output_size = 3
        
        self.model = Linear_QNet(self.input_size, self.hidden_size, self.output_size)
        self.trainer = QTrainer(self.model, learning_rate = LEARNING_RATE, gamma = self.gamma)
        # TODO : model, trainer
        
    def get_state(self, game):
        # current head position of snake in the game
        head = game.snake[0]
        
        # current 4 coordinates next to snake head
        point_left_of_head = Point(head.x - BLOCK_SIZE, head.y)
        point_right_of_head = Point(head.x + BLOCK_SIZE, head.y)
        point_up_of_head = Point(head.x, head.y - BLOCK_SIZE)
        point_down_of_head = Point(head.x, head.y + BLOCK_SIZE)
        
        # current snake head direction
        direction_left = game.direction == Direction.LEFT
        direction_right = game.direction == Direction.RIGHT
        direction_up = game.direction == Direction.UP
        direction_down = game.direction == Direction.DOWN
        
        # state values = [danger straight, danger right, danger left,
        #                 direction_left, direction_right, direction_up, direction_down,
        #                 food_left, food_right, food_up, food_down]
        
        state = [
                # Danger Straight
                # check if snake direction is right and collision point is also at right
                (direction_right and game.is_collision(point_right_of_head)) or
                # check if snake direction is left and collision point is also at left
                (direction_left and game.is_collision(point_left_of_head)) or
                # check if snake direction is up and collision point is also at up
                (direction_up and game.is_collision(point_up_of_head)) or
                # check if snake direction is down and collision point is also at down
                (direction_down and game.is_collision(point_down_of_head)),
                
                # Danger Right
                # check if snake direction is up and collision point is at right
                (direction_up and game.is_collision(point_right_of_head)) or
                # check if snake direction is down and collision point is at left
                (direction_down and game.is_collision(point_left_of_head)) or
                # check if snake direction is left and collision point is at up
                (direction_left and game.is_collision(point_up_of_head)) or
                # check if snake direction is right and collision point is at down
                (direction_right and game.is_collision(point_down_of_head)),
                
                # Danger left
                # check if snake direction is up and collision point is at right
                (direction_down and game.is_collision(point_right_of_head)) or
                # check if snake direction is down and collision point is at left
                (direction_up and game.is_collision(point_left_of_head)) or
                # check if snake direction is left and collision point is at up
                (direction_right and game.is_collision(point_up_of_head)) or
                # check if snake direction is right and collision point is at down
                (direction_left and game.is_collision(point_down_of_head)),
                
                # current direction of the snake
                direction_left, 
                direction_right, 
                direction_up, 
                direction_down,
                
                # Food location
                # food is present at left direction of snake's head
                game.food.x < game.head.x,
                # food is present at right direction of snake's head
                game.food.x > game.head.x,
                # food is present at up direction of snake's head
                game.food.y < game.head.y,
                # food is present at down direction of snake's head
                game.food.y > game.head.y
                ]
        
        return np.array(state, dtype = int)
        
        
    
    def remember(self, state, action, reward, next_state, done):
        """
        state  : current game state
        action : current game action
        reward : current game reward
        next_state : computed next state
        done : Flag value, whether the game is over or not
        """
        # popleft if MAX_MEMORY is reached
        self.memory.append((state, action, reward, next_state, done))
    
    def train_long_memory(self):
        # when we want to train over model on batches of data
        if len(self.memory) > BATCH_SIZE:
            # list of tuples
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory
        
        # extract the information from the mini sample into a proper tabular/matrix format
        states, actions, rewards, next_states, dones = zip(*mini_sample)
        # training on mini batch
        self.trainer.train_step(states, actions, rewards, next_states, dones)
    
    def train_short_memory(self, state, action, reward, next_state, done):
        # when we want to train our model on smaller steps like 1-5
        self.trainer.train_step(state, action, reward, next_state, done)
    
    def get_action(self, state):
        # random moves : tradeoff exploration / exploitation
        
        # epsilon is randomness parameter
        # epsilon is inversly proportional to no of games played
        self.epsilon = 80 - self.number_of_games
        # an empty state initialization
        next_action = [0, 0, 0]
        
        # random condition 
        if random.randint(0, 200) < self.epsilon:
            # a random move
            move = random.randint(0, 2)
            next_action[move] = 1
        else:
            # current state Pytorch tensor
            state_zero = torch.tensor(state, dtype = torch.float)
            # prediction based on previous state
            prediction = self.model(state_zero)
            
            # prediction is a list of raw values, converting that to index of maximum number
            move = torch.argmax(prediction).item()  
            next_action[move] = 1
        
        return next_action
    
def train():
    plot_scores = [] # list to keep track of scores
    plot_mean_scores = [] # list to keep track of mean scores
    total_score = 0
    best_score = 0
    
    agent = Agent()
    game = SnakeGameAI()
    
    while True:
        # get current state
        current_state = agent.get_state(game)
        
        # move based on current state
        next_action = agent.get_action(current_state)
        
        # perform move and get new state
        reward, done, score = game.play_step(next_action)
        new_state = agent.get_state(game)
        
        # train on short memory
        agent.train_short_memory(current_state, next_action, reward, new_state, done)
        
        # remember
        agent.remember(current_state, next_action, reward, new_state, done)
        
        # if game over
        if done:
            # train the long long memory
            # plot the results
            
            # resetting the game first
            game.reset()
            
            # increment the no of games played by agent
            agent.number_of_games += 1
            
            agent.train_long_memory()
            
            if score > best_score:
                best_score = score
                
                # whenever get a high score, save that model
                agent.model.save()
            
            print("Game ", agent.number_of_games, "Score ", score, "Best Score ", best_score)
            
            # plotting
            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.number_of_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)
            
if __name__ == "__main__":
    train()
        


