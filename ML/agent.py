import chess


class Agent:
    # model_id is the model id in mongoDB to the model file
    def __init__(self, model_id: str):
        self.model = model_id  # TODO update this to retreive model from database

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
