# evaluate the model on player data to see how well it matches the player
# after testing, save the results to local file

import torch
import torch.nn as nn


class EvaluateModel:
    def __init__(self, model: nn.Module, test_x: torch.Tensor, test_y: torch.Tensor):
        '''
        model is the model to test
        test_x is the features to test the model on
        test_y is the y to test the model on
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
            mae = nn.L1Loss()(outputs, self.y) 

        return mae


    def save_results(self, mse: float, mae: float):
        '''
        save the results to a local file in model_evals

        '''
        with open("model_evals/results.txt", "a") as f:
            f.write(f"MSE: {mse}, MAE: {mae}\n")
