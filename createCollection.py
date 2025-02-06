from pymongo import MongoClient

# Conéctate a MongoDB Atlas con tu URI
MONGO_URI = "mongodb+srv://tictactoe-admin:tictactoe1234@tictactoe-ruben-xavier.k9psb.mongodb.net/?retryWrites=true&w=majority&appName=TicTacToe-Ruben-Xavier"
client = MongoClient(MONGO_URI)

# Crea la base de datos y la colección con las iniciales de los jugadores
db = client["tic_tac_toe"]
jugadores = ["rrl", "xfm"]
nombre_coleccion = "-".join(jugadores)

# Crea la colección solo si no existe
if nombre_coleccion not in db.list_collection_names():
    db.create_collection(nombre_coleccion)
    print(f"Colección '{nombre_coleccion}' creada exitosamente.")
else:
    print(f"La colección '{nombre_coleccion}' ya existe.")