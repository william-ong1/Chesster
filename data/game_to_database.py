from pymongo import MongoClient
from .parse_pgn import ParsePGN
from .board_state import BoardState


class GameToDatabase:

    def __init__(self, username):
        self.uri = "<Insert URI here>"
        self.username = {"username": username}

    def upload_pgn(self, filename):
        client = MongoClient(self.uri)
        user = self.fetch_user()
        try:

            database = client.get_database("chesster")
            board_states = database.get_collection("board_states")
            parser = ParsePGN()

            parser.parse_file(filename)

            to_upload = []
            for game in parser.parsed_games:
                for game_state in game:
                    doc = self._to_document(game_state)
                    to_upload.append(doc)

            total_docs = board_states.count_documents({}) + len(to_upload)

            for doc in to_upload:
                fen_exists = False
                for user_game_state in user["game_states"]:
                    if user_game_state["fen"] == game_state.fen:
                        self.increment_occurrences(
                            user_game_state, total_docs, user["_id"]
                        )
                        fen_exists = True
                        break

                if not fen_exists:
                    board_states.update_one

            for user_game_state in user["game_states"]:
                user_game_state
            fen = user["game_states"][0]["fen"]
            print(f"Fen: {fen}")
            # print(game_state[0])

            print(to_upload)
            board_states.insert_many(to_upload)

        except OSError as e:
            raise OSError(
                "Unable to upload the document due to the following error: ", e
            )

        finally:
            client.close()

    def _to_document(self, board_state: BoardState):
        bson_pieces = []
        for piece in board_state.pieces:
            bson_pieces.append(
                {
                    "color": piece.piece_color.value,
                    "type": piece.piece_type.value,
                }
            )

        return {
            "fen": board_state.fen,
            "state": bson_pieces,
            "next_move": board_state.move,
            "features": "to be implemented",
        }

    def fetch_user(self):
        client = MongoClient(self.uri)
        try:
            database = client.get_database("chesster")
            user_data = database.get_collection("user_data")

            print("Looking for: " + str(self.username))
            user = user_data.find_one(self.username)
            print(user)
        except FileNotFoundError as e:
            raise FileNotFoundError(
                "Unable to find the document due to the following error: ", e
            )
        finally:
            client.close()

        return user

    def increment_occurrences(self, old_state, total_docs, userid):
        client = MongoClient(self.uri)
        try:
            database = client.get_database("chesster")
            user_data = database.get_collection("user_data")

            new_occurrences = old_state["occurrences"] + 1
            new_y = new_occurrences / total_docs

            new_game_state = {
                "fen": old_state["fen"],
                "occurrences": new_occurrences,
                "y": new_y,
            }

            user_data.update_one({"_id": userid}, new_game_state)
        except FileNotFoundError as e:
            raise FileNotFoundError(
                "Unable to find the document due to the following error: ", e
            )
        finally:
            client.close()
