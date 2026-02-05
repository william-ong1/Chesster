# code for training the model from a given architecture, using supervised learning and a weighted sum of the player's data
# and the evaluation of a preexisting chess engine.

import torch
import torch.nn as nn
import chess

class Training:
    
    def __init__(self, model: str, data: str, engine: str):