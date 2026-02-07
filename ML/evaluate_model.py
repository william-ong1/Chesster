# evaluate the model on player data to see how well it matches the player
# pull data from mongoDB and use it to test the model.
# after testing, save the results to mongoDB

import torch
import torch.nn as nn
import chess
import torch.utils.data as DataLoader
import pymongo

class EvaluateModel:
    def __init__(self, model: nn.Module, dataloader: DataLoader):

        self.model = model
        self.data = dataloader


    def MSE(self) -> float:
        
        

