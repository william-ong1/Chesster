# (C) Chesster. Written by Shreyan Mitra, William Ong, Mason Tepper, Lebam Amare, Raghav Ramesh, and Danyuan Wang

import chess
import os
import sys
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

game_bp = Blueprint("game", __name__)
