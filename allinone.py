import tkinter as tk
from tkinter import messagebox
from pymongo import MongoClient
import random
import threading

# MongoDB Connection
MONGO_URI = "mongodb+srv://tictactoe-admin:tictactoe1234@tictactoe-ruben-xavier.k9psb.mongodb.net/tictactoe?retryWrites=true&w=majority&appName=TicTacToe-Ruben-Xavier"
client = MongoClient(MONGO_URI)
db = client.tictactoe
games_collection = db.games

# GUI Setup
root = tk.Tk()
root.title("Tic-Tac-Toe")

# Global variables
game_id = None
polling = False

def generate_game_id():
    while True:
        game_id = random.randint(100000, 999999)
        if not games_collection.find_one({"gameId": game_id}):
            return game_id

def create_game():
    global game_id
    game_id = generate_game_id()
    new_game = {
        "gameId": game_id,
        "board": [None] * 9,
        "currentPlayer": "X",
        "winner": None,
        "isDraw": False
    }
    games_collection.insert_one(new_game)
    messagebox.showinfo("New Game", f"Game created! Game ID: {game_id}")
    show_game_screen()

def join_game():
    global game_id
    try:
        game_id = int(game_id_entry.get().strip())
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid Game ID.")
        return

    if games_collection.find_one({"gameId": game_id}):
        show_game_screen()
    else:
        messagebox.showerror("Error", "Game not found.")

def show_game_screen():
    start_frame.pack_forget()
    game_id_label.config(text=f"Game ID: {game_id}")
    update_board()
    game_frame.pack()

def make_move(index):
    game = games_collection.find_one({"gameId": game_id})
    if not game:
        messagebox.showerror("Error", "Game not found.")
        return

    if game["winner"] or game["isDraw"] or game["board"][index] is not None:
        messagebox.showerror("Error", "Invalid move.")
        return

    game["board"][index] = game["currentPlayer"]
    winner = check_winner(game["board"])
    if winner:
        game["winner"] = winner
    elif None not in game["board"]:
        game["isDraw"] = True
    game["currentPlayer"] = "O" if game["currentPlayer"] == "X" else "X"
    games_collection.update_one({"gameId": game_id}, {"$set": game})
    update_board()

def update_board():
    game = games_collection.find_one({"gameId": game_id})
    if game:
        for i, cell in enumerate(game["board"]):
            buttons[i].config(text=cell if cell else " ", state=tk.NORMAL if not cell and not game["winner"] and not game["isDraw"] else tk.DISABLED)
        if game["winner"]:
            status_label.config(text=f"Winner: {game['winner']}")
        elif game["isDraw"]:
            status_label.config(text="It's a draw!")
        else:
            status_label.config(text=f"Current Player: {game['currentPlayer']}")

def check_winner(board):
    winning_combinations = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]]
    for combo in winning_combinations:
        if board[combo[0]] == board[combo[1]] == board[combo[2]] and board[combo[0]] is not None:
            return board[combo[0]]
    return None

def watch_game():
    pipeline = [{"$match": {"operationType": "update"}}]
    with games_collection.watch(pipeline) as stream:
        for change in stream:
            if change["fullDocument"]["gameId"] == game_id:
                update_board()

def start_watch_thread():
    threading.Thread(target=watch_game, daemon=True).start()

# GUI Components
start_frame = tk.Frame(root)
tk.Label(start_frame, text="Enter Game ID:", font=("Arial", 14)).pack(pady=10)
game_id_entry = tk.Entry(start_frame, font=("Arial", 14))
game_id_entry.pack(pady=10)
tk.Button(start_frame, text="Join Game", font=("Arial", 14), command=join_game).pack(pady=10)
tk.Button(start_frame, text="Create New Game", font=("Arial", 14), command=create_game).pack(pady=10)
start_frame.pack()

game_frame = tk.Frame(root)
game_id_label = tk.Label(game_frame, text="Game ID: None", font=("Arial", 14))
game_id_label.grid(row=0, column=0, columnspan=3)
status_label = tk.Label(game_frame, text="Current Player: X", font=("Arial", 14))
status_label.grid(row=1, column=0, columnspan=3)
buttons = [tk.Button(game_frame, text=" ", font=("Arial", 24), width=5, height=2, command=lambda i=i: make_move(i)) for i in range(9)]
for i, button in enumerate(buttons):
    button.grid(row=i//3+2, column=i%3)
game_frame.pack()

if __name__ == "__main__":
    start_watch_thread()
    root.mainloop()