# main function for the ML pipeline, it should bring the data from mongoDB and split it into training and testing data.
# it should then train the model and test it, it should also save the model's evaluation metrics, to local.

import pymongo
from training import Training
from evaluate_model import EvaluateModel
from torch.utils.data import DataLoader
from sklearn.model_selection import train_test_split
import torch
import os


def main(user_id: str):
    # connect to mongoDB
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["chesster"]
    user_data = db["user_data"]
    models = db["chess_models"]
    boards = db["board_states"]

    # get the game data
    user = user_data.find({"user_id": user_id})
    user_game_boards = user["game_boards"]

    # grab x and y from the game data
    features = []
    y = []
    for board_id, number_appearances, y_value in user_game_boards:
        features = boards.find({"board_id": board_id})
        y.append(y_value)
    
    features = torch.tensor(features)
    y = torch.tensor(y)

    # split into training and testing data
    features_train, features_test, y_train, y_test = train_test_split(features, y, test_size=0.2, random_state=42)
    dataloader_train = DataLoader(features_train, y_train, batch_size=10, shuffle=True)

    
    training = Training(
        architecture="3_layer_nn", 
        dataloader=dataloader_train, 
        optim_class=torch.optim.Adam, 
        loss_fn=torch.nn.MSELoss(), 
        learning_rate=0.001, 
        num_epochs=10, 
        log_every=10, 
        verbose=True, 
        device="cpu"
        )
    training.train()
    model = training.model
    evaluation = EvaluateModel(model, features_test, y_test)
    mse = evaluation.MSE()
    mae = evaluation.MAE()
    evaluation.save_results(mse, mae)
    if models.find_one({"user_id": user_id}) != None:
        models.update_one({"user_id": user_id}, {"$set": {"model": model.state_dict()}})
    else:
        models.insert_one({"user_id": user_id, "model": model.state_dict(),})

if __name__ == "__main__":
    main("123")