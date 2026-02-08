# (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang
# main function for the ML pipeline, it should bring the data from mongoDB and split it into training and testing data.
# it should then train the model and test it, it should also save the model's evaluation metrics, to local.

import pymongo
import ML.training as training
import ML.test as test
import os
