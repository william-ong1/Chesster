# (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
# code to take a model from ML\models and wrap it in a class that can be used to play chess.
# this class should take a model for initaliztion and take a board state as input and return a move.
# the class should also be able to take a move as input and update the board state.
import chess


class Agent:
    # model_id is the model id in mongoDB to the model file
    def __init__(self, model_id: str):
        self.model = model_id  # TODO update this to retreive model from database
        self.board = chess.Board()

        if self.model is None:
            raise ValueError(f"User does not have a model with id {model_id}")

        self.model.eval()

    def get_move(self, board: chess.Board) -> chess.Move:
        """
        takes in a board state
        goes through all legal moves
        evaluates each move using model
        returns the best move
        """
        player_move = None
        if board.move_stack:
            player_move = board.move_stack[-1]
        if player_move is not None:
            self.board.push(player_move)

        legal_moves = list(board.legal_moves)
        best_move = None
        best_value = -float("inf")

        for move in legal_moves:
            board.push(move)
            value = self.model(
                board
            ).item()  # TODO update this to transform board states to features for model input
            board.pop()
            if value > best_value:
                best_move = move
                best_value = value

        return best_move

    def make_move(self, move: chess.Move):
        if move in self.board.legal_moves:
            self.board.push(move)

    def get_board(self):
        return self.board
