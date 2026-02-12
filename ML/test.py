# evaluate the model on player data to see how well it matches the player
# pull data from mongoDB and use it to test the model.
# after testing, save the results to mongoDB

import torch
import torch.nn as nn
import chess
import torch.utils.data as DataLoader
import pymongo

class Testing:
    def __init__(self, model: nn.Module, dataloader: DataLoader):
        '''
        model is the model to test
        dataloader is the dataloader to test the model on
        '''
        self.model = model
        self.data = dataloader
        self.X = []
        self.y = []
        

    def MSE(self) -> float:
        '''
        get the data from the database
        convert the data into a dataloader
        test the model on the dataloader
        return the MSE of the model

        '''
        self.data = self.collection.find()
        
        self.model.eval()
        with torch.no_grad():
            outputs = self.model(X)
            mse = nn.MSELoss()(outputs, y)
        
        return mse

    def R2(self) -> float:
        '''
        get the data from the database
        convert the data into a dataloader
        test the model on the dataloader
        return the R2 of the model
        '''
        self.data = self.collection.find()
        X = []
        y = []
        for game in self.data:
            X.append(game["extracted_board_state"])
            y.append(game["value"])
        X = torch.tensor(X)
        y = torch.tensor(y)
        self.data = DataLoader(X, y, batch_size=100, shuffle=True)
        self.model.eval()
        with torch.no_grad():
            outputs = self.model(X)
            r2 = nn.R2Loss()(outputs, y)
        return r2
    
    def MAE(self) -> float:
        '''
        get the data from the database
        convert the data into a dataloader
        test the model on the dataloader
        return the MAE of the model
        '''
        self.data = self.collection.find()
        X = []
        y = []
        for game in self.data:
            X.append(game["extracted_board_state"])
            y.append(game["value"])
        X = torch.tensor(X)
        y = torch.tensor(y)
        self.data = DataLoader(X, y, batch_size=100, shuffle=True)
        self.model.eval()
        with torch.no_grad():
            outputs = self.model(X)
            mae = nn.MAELoss()(outputs, y) 

        return mae


    def save_results(self, mse: float, r2: float, mae: float):
        '''
        save the results to a local file in model_evals

        '''
        with open("model_evals/results.txt", "a") as f:
            f.write(f"MSE: {mse}, R2: {r2}, MAE: {mae}\n")