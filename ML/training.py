# code for training the model from a given architecture, using supervised learning and a weighted sum of the player's data
# and the evaluation of a preexisting chess engine.
# pull data from mongoDB and use it to train the model.
# after training, save the model to mongoDB

import torch
import torch.nn as nn
import chess
import torch.utils.data as DataLoader

class Training:
    # architecture is the architecture of the model to train from the model_architecture folder

    def __init__(self, architecture: str, dataloader: DataLoader):
        #TODO
        pass

    def train(self):
        #TODO
        pass



    