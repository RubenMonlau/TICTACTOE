import tkinter as tk
from tkinter import messagebox
import requests
import threading

# Backend API URL
API_URL = "http://127.0.0.1:5000/api/games"

# Global variables
game_id = None
polling = False

# Create a new game
def create_game():
    global game_id, polling
    response = requests.post(API_URL)
    if response.status_code == 201:
        game_id = response.json()["gameId"]
        messagebox.showinfo("New Game", f"Game created! Game ID: {game_id}")
        polling = True
        threading.Thread(target=poll_game_state, daemon=True).start()  # Start polling
        show_game_screen()

# Join an existing game
def join_game():
    global game_id, polling
    try:
        game_id = int(game_id_entry.get().strip())  # Ensure the game ID is an integer
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid 6-digit Game ID.")
        return

    response = requests.get(f"{API_URL}/{game_id}")
    if response.status_code == 200:
        polling = True
        threading.Thread(target=poll_game_state, daemon=True).start()  # Start polling
        show_game_screen()
    else:
        messagebox.showerror("Error", "Game not found. Please check the Game ID.")

# Show the game screen
def show_game_screen():
    # Hide the start screen
    start_frame.pack_forget()

    # Show the game screen
    game_id_label.config(text=f"Game ID: {game_id}")
    update_board()
    game_frame.pack()

# Make a move
def make_move(index):
    response = requests.post(f"{API_URL}/{game_id}/move", json={"index": index})
    if response.status_code == 200:
        update_board()
    else:
        messagebox.showerror("Error", "Failed to make move.")

# Update the board
def update_board():
    response = requests.get(f"{API_URL}/{game_id}")
    if response.status_code == 200:
        game = response.json()
        for i, cell in enumerate(game["board"]):
            buttons[i].config(text=cell if cell else " ", state=tk.NORMAL if not cell and not game["winner"] and not game["isDraw"] else tk.DISABLED)
        if game["winner"]:
            status_label.config(text=f"Winner: {game['winner']}")
            polling = False  # Stop polling when the game is over
        elif game["isDraw"]:
            status_label.config(text="It's a draw!")
            polling = False  # Stop polling when the game is over
        else:
            status_label.config(text=f"Current Player: {game['currentPlayer']}")
    else:
        messagebox.showerror("Error", "Failed to fetch game state.")

# Poll the game state periodically
def poll_game_state():
    while polling:
        update_board()
        root.update()  # Update the GUI
        threading.Event().wait(2)  # Poll every 2 seconds

# GUI Setup
root = tk.Tk()
root.title("Tic-Tac-Toe")

# Start Screen
start_frame = tk.Frame(root)

# Game ID Entry
tk.Label(start_frame, text="Enter Game ID:", font=("Arial", 14)).pack(pady=10)
game_id_entry = tk.Entry(start_frame, font=("Arial", 14))
game_id_entry.pack(pady=10)

# Join Game Button
tk.Button(start_frame, text="Join Game", font=("Arial", 14), command=join_game).pack(pady=10)

# Create Game Button
tk.Button(start_frame, text="Create New Game", font=("Arial", 14), command=create_game).pack(pady=10)

start_frame.pack()

# Game Screen
game_frame = tk.Frame(root)

# Game ID Label
game_id_label = tk.Label(game_frame, text="Game ID: None", font=("Arial", 14))
game_id_label.grid(row=0, column=0, columnspan=3)

# Status Label
status_label = tk.Label(game_frame, text="Current Player: X", font=("Arial", 14))
status_label.grid(row=1, column=0, columnspan=3)

# Buttons for the board
buttons = []
for i in range(9):
    row, col = divmod(i, 3)
    button = tk.Button(game_frame, text=" ", font=("Arial", 24), width=5, height=2,
                       command=lambda i=i: make_move(i))
    button.grid(row=row + 2, column=col)
    buttons.append(button)

# Back to Start Screen Button
tk.Button(game_frame, text="Back to Start", font=("Arial", 14), command=lambda: [game_frame.pack_forget(), start_frame.pack()]).grid(row=5, column=0, columnspan=3)

# Initially show the start screen
start_frame.pack()

root.mainloop()