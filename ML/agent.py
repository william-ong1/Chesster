# (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
# code to take a model from ML\models and wrap it in a class that can be used to play chess. 
# this class should take a model for initaliztion and take a board state as input and return a move.
# the class should also be able to take a move as input and update the board state.
# include a search function in the agent class with alpha beta pruning.

import torch
import chess

class Agent:
    # model_id is the model id in mongoDB to the model file
    def __init__(self, model_id: str):
        self.model = torch.load(model)
        self.board = chess.Board()

    def get_move(self, board: chess.Board) -> chess.Move:
        #TODO
        pass

    def make_move(self, move: chess.Move):
        #TODO
        pass

    def get_board(self) -> chess.Board:
        #TODO
        pass