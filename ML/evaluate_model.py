# evaluate the model on player data to see how well it matches the player
# pull data from mongoDB and use it to test the model.
# after testing, save the results to mongoDB

import torch
import torch.nn as nn
import chess
from torch.utils.data import DataLoader
import pymongo

class EvaluateModel:
    def __init__(self, model: nn.Module, test_x: torch.Tensor, test_y: torch.Tensor):
        '''
        model is the model to test
        dataloader is the dataloader to test the model on
        '''
        self.model = model
        self.X = test_x
        self.y = test_y
        

    def MSE(self) -> float:
        '''
        get the data from the database
        convert the data into a dataloader
        test the model on the dataloader
        return the MSE of the model

        '''
        
        self.model.eval()
        with torch.no_grad():
            outputs = self.model(self.X)
            mse = nn.MSELoss()(outputs, self.y)
        
        return mse

    def R2(self) -> float:
        '''
        get the data from the database
        convert the data into a dataloader
        test the model on the dataloader
        return the R2 of the model
        '''
        self.model.eval()
        with torch.no_grad():
            outputs = self.model(self.X)
            r2 = nn.R2Loss()(outputs, self.y)
        return r2
    
    def MAE(self) -> float:
        '''
        get the data from the database
        convert the data into a dataloader
        test the model on the dataloader
        return the MAE of the model
        '''
        self.model.eval()
        with torch.no_grad():
            outputs = self.model(self.X)
            mae = nn.MAELoss()(outputs, self.y) 

        return mae


    def save_results(self, mse: float, r2: float, mae: float):
        '''
        save the results to a local file in model_evals

        '''
        with open("model_evals/results.txt", "a") as f:
            f.write(f"MSE: {mse}, R2: {r2}, MAE: {mae}\n")
