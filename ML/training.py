# (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
# Code for training the model from a given architecture, using supervised learning and a weighted sum of the player's data
# and the evaluation of a preexisting chess engine (Stockfish).
# Pull data from MongoDB and use it to train the model.
# After training, save the model to MongoDB.

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.optim import Optimizer
from typing import Optional, Type
from ML.model_architectures import ThreeLayerNN  # Import the 3 layer neural network architecture
import uuid

class Training:

    def __init__(
            self,
            architecture: str,
            dataloader: DataLoader,
            optim_class: Type[Optimizer],
            val_dataloader: Optional[DataLoader] = None,
            loss_fn: nn.Module = nn.MSELoss(),
            learning_rate: float = 0.001,
            num_epochs: int = 10,
            log_every: int = 10,
            verbose: bool = True,
            device: str = 'cpu'
    ):
        
        """
        Configure a training run.

        Args:
            architecture: Model architecture type to load.
            dataloader: Training data loader.
            optim_class: Optimizer class (e.g., torch.optim.Adam).
            val_dataloader: Optional validation data loader.
            loss_fn: Loss function to optimize.
            learning_rate: Optimizer learning rate.
            num_epochs: Number of training epochs.
            log_every: Step interval for logging.
            verbose: Whether to print training progress.
            device: Type of device to use ('cpu' or 'cuda').
        """

        self.architecture = architecture
        self.dataloader = dataloader
        self.val_dataloader = val_dataloader
        self.loss_fn = loss_fn
        self.learning_rate = learning_rate
        self.num_epochs = num_epochs
        self.log_every = log_every
        self.verbose = verbose
        self.device = torch.device(device)
        
        # Initialize model based on architecture name
        self.model = self._load_architecture(architecture)
        self.model = self.model.to(self.device)

        self.optimizer = optim_class(self.model.parameters(), defaults={'lr': self.learning_rate})
        self.model_id = str(uuid.uuid4())


    def _load_architecture(self, architecture: str) -> nn.Module:

        """
        Load a model architecture by the given name.

        Args:
            architecture: Name of architecture to load.

        Returns:
            An instance of the requested model architecture.
        """

        if architecture == "3_layer_nn":
            return ThreeLayerNN() # TODO: figure out function call and temp. params
        else:
            raise ValueError(f"Unknown architecture: {architecture}. "
                           f"Available: '3_layer_nn'")
        

    def train(self):

        """
        Train the model using the configured parameters and data.
        """

        self.model.train()

        for epoch in range(self.num_epochs):

            running_loss = 0.0

            for batch_idx, (data, target) in enumerate(self.dataloader):

                data, target = data.to(self.device), target.to(self.device)
                self.optimizer.zero_grad()

                output = self.model(data)
                loss = self.loss_fn(output, target)
                loss.backward()

                self.optimizer.step()
                running_loss += loss.item()

                if batch_idx % self.log_every == 0 and self.verbose:
                    print(f"Epoch {epoch+1}, Batch {batch_idx}, Loss: {running_loss/self.log_every}")
                    running_loss = 0.0


        if self.val_dataloader is not None:
            self._validate()



    def _validate(self):

        """
        Validate the model on the validation dataset, if provided.
        """

        if self.val_dataloader is None:
            return
        
        self.model.eval()
        val_loss = 0.0

        with torch.no_grad():
            for data, target in self.val_dataloader:
                data, target = data.to(self.device), target.to(self.device)
                output = self.model(data)
                loss = self.loss_fn(output, target)
                val_loss += loss.item()

        avg_val_loss = val_loss / len(self.val_dataloader)
        if self.verbose:
            print(f"Validation Loss: {avg_val_loss}")



    def save_model(self, model_id: str):
        
        # make API call to backend to save the model with model_id + user_id
        pass
        
