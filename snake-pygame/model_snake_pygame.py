# -*- coding: utf-8 -*-
"""
Created on Sun Jul 25 23:51:44 2021

@author: P Akash
"""

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import os

class Linear_QNet(nn.Module):
    """
    Feed forward neural network consists of input, hidden and output layer
    """
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, output_size)
        
    def forward(self, x):
        x = F.relu(self.linear1(x))
        x = self.linear2(x)
        return x
    
    def save(self, filename = "model.pth"):
        model_folder_path = "./snake_pygame_models"
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)
        
        filename = os.path.join(model_folder_path, filename)
        torch.save(self.state_dict(), filename)
        
class QTrainer():
    def __init__(self, model, learning_rate, gamma):
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.model = model
        self.optimizer = optim.Adam(model.parameters(), lr = self.learning_rate)
        self.criterion = nn.MSELoss()
        
    def train_step(self, current_state, next_action, reward, new_state, done):
        current_state = torch.tensor(current_state, dtype = torch.float)
        next_action = torch.tensor(next_action, dtype = torch.float)
        reward = torch.tensor(reward, dtype = torch.float)
        new_state = torch.tensor(new_state, dtype = torch.float)
        
        # check if the values are in batches or a single tuple
        if len(current_state.shape) == 1:
            # if len(current_state.shape) == 1, then current_state shape will be like (n,)
            # we want to convert (n,) into (1, n), where 1 is batch size
            current_state = torch.unsqueeze(current_state, dim = 0)
            next_action = torch.unsqueeze(next_action, dim = 0)
            reward = torch.unsqueeze(reward, dim = 0)
            new_state = torch.unsqueeze(new_state, dim = 0)
            done = (done, )
        
        # 1. predicted Q values with the current state
        # predicted action based on current state, also called as Q value
        predicted_action = self.model(current_state) 
        # returns an tensor of size (1,3) raw values
        
        # 2. Q_new = reward + gamma * max(next predicted Q value)
        # reward = scalar value
        # gamma = scaler value
        # model(new_state) = next predicted Q value = (1,3)
        # max(model(new_state)) = scaler value
        # to convert this scaler value same as that of pred
        # predicted_action.clone()
        # preds[argmax(predicted_action)] = Q_new
        target = predicted_action.clone() # shape (1,3)
        for idx in range(len(done)): # because batches
            Q_new = reward[idx]
            
            if not done[idx]:
                Q_new = reward[idx] + self.gamma * torch.max(self.model(new_state[idx]))
            
            target[idx][torch.argmax(next_action).item()] = Q_new
        
        # backpropagation
        # error and loss function
        self.optimizer.zero_grad()
        loss = self.criterion(target, predicted_action)
        loss.backward()
        self.optimizer.step()
        
        
        
        
            