# evaluate the model on player data to see how well it matches the player
# pull data from mongoDB and use it to test the model.
# after testing, save the results to mongoDB

import torch
import torch.nn as nn
import chess
import torch.utils.data as DataLoader

class Testing:
    def __init__(self, model_id: str, dataloader: DataLoader):
        self.model = torch.load(model_id)
        self.data = self.get_data()