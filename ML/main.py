"""
main function for the ML pipeline, it should bring the data from mongoDB
and split it into training and testing data. It should then train the model
and test it, it should also save the model's evaluation metrics, to local.
"""

import pymongo
from training import Training
from evaluate_model import EvaluateModel
from torch.utils.data import DataLoader
import torch

# NOTE: Commented this out to pass linter checks (it's currently unused)
# import os


def main(user_id: str):
    # connect to mongoDB
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["chesster"]
    game_data = db["game_data"]
    models = db["models"]

    # get the game data
    game_data = game_data.find({"user_id": user_id})
    # split the data into training and testing data
    features = []
    y = []
    for board in game_data:
        features.append(board["features"])
        y.append(board["y"])

    features = torch.tensor(features)
    y = torch.tensor(y)

    dataloader = DataLoader(features, y, batch_size=10, shuffle=True)
    training = Training(
        architecture="3_layer_nn",
        dataloader=dataloader,
        optim_class=torch.optim.Adam,
        loss_fn=torch.nn.MSELoss(),
        learning_rate=0.001,
        num_epochs=10,
        log_every=10,
        verbose=True,
        device="cpu",
    )
    training.train()
    # TODO: update with a proper x value
    evaluation = EvaluateModel(training.model, None, y)
    evaluation.evaluate()
    training.save_model(models)


if __name__ == "__main__":
    main("123")
