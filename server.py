from flask import Flask, request, jsonify
from pymongo import MongoClient
import random

app = Flask(__name__)

# MongoDB Connection
MONGO_URI = "mongodb+srv://tictactoe-admin:tictactoe1234@tictactoe-ruben-xavier.k9psb.mongodb.net/tictactoe?retryWrites=true&w=majority&appName=TicTacToe-Ruben-Xavier"
client = MongoClient(MONGO_URI)
db = client.tictactoe
games_collection = db.games

# Helper function to generate a unique 6-digit game ID
def generate_game_id():
    while True:
        game_id = random.randint(100000, 999999)  # Generate a 6-digit number
        if not games_collection.find_one({"gameId": game_id}):  # Ensure it's unique
            return game_id

# Helper function to check for a winner
def check_winner(board):
    winning_combinations = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
        [0, 4, 8], [2, 4, 6]              # Diagonals
    ]
    for combo in winning_combinations:
        if board[combo[0]] == board[combo[1]] == board[combo[2]] and board[combo[0]] is not None:
            return board[combo[0]]  # Return the winner (X or O)
    return None

# Create a new game
@app.route("/api/games", methods=["POST"])
def create_game():
    game_id = generate_game_id()  # Generate a unique 6-digit game ID
    new_game = {
        "gameId": game_id,  # Store the 6-digit game ID
        "board": [None] * 9,  # 3x3 Tic-Tac-Toe board
        "currentPlayer": "X",  # X starts first
        "winner": None,
        "isDraw": False
    }
    games_collection.insert_one(new_game)
    return jsonify({"gameId": game_id}), 201

# Get game state
@app.route("/api/games/<int:game_id>", methods=["GET"])
def get_game(game_id):
    game = games_collection.find_one({"gameId": game_id})
    if not game:
        return jsonify({"error": "Game not found"}), 404
    game["_id"] = str(game["_id"])  # Convert ObjectId to string
    return jsonify(game)

# Make a move
@app.route("/api/games/<int:game_id>/move", methods=["POST"])
def make_move(game_id):
    data = request.json
    index = data.get("index")  # Cell index (0-8)
    if index is None or index < 0 or index > 8:
        return jsonify({"error": "Invalid move"}), 400

    game = games_collection.find_one({"gameId": game_id})
    if not game:
        return jsonify({"error": "Game not found"}), 404

    if game["winner"] or game["isDraw"]:
        return jsonify({"error": "Game is already over"}), 400

    if game["board"][index] is not None:
        return jsonify({"error": "Cell is already occupied"}), 400

    # Update the board
    game["board"][index] = game["currentPlayer"]

    # Check for a winner
    winner = check_winner(game["board"])
    if winner:
        game["winner"] = winner
    elif None not in game["board"]:  # Check for a draw
        game["isDraw"] = True

    # Switch players
    game["currentPlayer"] = "O" if game["currentPlayer"] == "X" else "X"

    # Save the updated game state
    games_collection.update_one({"gameId": game_id}, {"$set": game})
    game["_id"] = str(game["_id"])  # Convert ObjectId to string
    return jsonify(game)

if __name__ == "__main__":
    app.run(debug=True)