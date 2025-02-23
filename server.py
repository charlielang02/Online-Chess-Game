import socket
from _thread import *
from board import Board
import pickle
import time

MAX_CONNECTIONS = 6
GAME_TIME_LIMIT = 900
BUFFER_SIZE = 8192 *3

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server = "localhost"
port = 5555

server_ip = socket.gethostbyname(server)

try:
    s.bind((server, port))

except socket.error as e:
    print(str(e))

s.listen()
print("[START] Waiting for a connection")

connections = 0

games = {0:Board(8, 8)}

spectartor_ids = [] 
specs = 0

def read_specs():
    """
    Reads the spectator IDs from the specs.txt file and stores them in the global list `spectartor_ids`.
    If the file does not exist, it creates a new one.
    """
    
    global spectartor_ids

    spectartor_ids = []
    try:
        with open("specs.txt", "r") as f:
            for line in f:
                spectartor_ids.append(line.strip())
    except:
        print("[ERROR] No specs.txt file found, creating one...")
        open("specs.txt", "w")


def threaded_client(conn, game, spec=False):
    """
    Handles communication with a client (player or spectator) in a separate thread.
    
    :param conn: The connection object representing the client connection.
    :param game: The game ID associated with the game the client is joining.
    :param spec: A boolean flag indicating whether the client is a spectator (True) or a player (False).
    """
    
    global pos, games, currentId, connections, specs

    if not spec:
        name = None
        bo = games[game]

        if connections % 2 == 0:
            currentId = "w"
        else:
            currentId = "b"

        bo.start_user = currentId

        # Pickle the object and send it to the server
        data_string = pickle.dumps(bo)

        if currentId == "b":
            bo.ready = True
            bo.startTime = time.time()

        conn.send(data_string)
        connections += 1

        while True:
            if game not in games:
                break

            try:
                d = conn.recv(BUFFER_SIZE)
                data = d.decode("utf-8")
                if not d:
                    break
                else:
                    if data.count("select") > 0:
                        all = data.split(" ")
                        col = int(all[1])
                        row = int(all[2])
                        color = all[3]
                        bo.select(col, row, color)

                    if data == "winner b":
                        bo.winner = "b"
                        print("[GAME] Player b won in game", game)
                    if data == "winner w":
                        bo.winner = "w"
                        print("[GAME] Player w won in game", game)

                    if data == "update moves":
                        bo.update_moves()

                    if data.count("name") == 1:
                        name = data.split(" ")[1]
                        if currentId == "b":
                            bo.p2Name = name
                        elif currentId == "w":
                            bo.p1Name = name

                    if bo.ready:
                        if bo.turn == "w":
                            bo.time1 = GAME_TIME_LIMIT - (time.time() - bo.startTime) - bo.storedTime1
                        else:
                            bo.time2 = GAME_TIME_LIMIT - (time.time() - bo.startTime) - bo.storedTime2

                    sendData = pickle.dumps(bo)

                conn.sendall(sendData)

            except Exception as e:
                print(e)
        
        connections -= 1
        try:
            del games[game]
            print("[GAME] Game", game, "ended")
        except:
            pass
        print("[DISCONNECT] Player", name, "left game", game)
        conn.close()

    else:
        available_games = list(games.keys())
        game_ind = 0
        bo = games[available_games[game_ind]]
        bo.start_user = "s"
        data_string = pickle.dumps(bo)
        conn.send(data_string)

        while True:
            available_games = list(games.keys())
            bo = games[available_games[game_ind]]
            try:
                d = conn.recv(128)
                data = d.decode("utf-8")
                if not d:
                    break
                else:
                    try:
                        if data == "forward":
                            print("[SPECTATOR] Moved Games forward")
                            game_ind += 1
                            if game_ind >= len(available_games):
                                game_ind = 0
                        elif data == "back":
                            print("[SPECTATOR] Moved Games back")
                            game_ind -= 1
                            if game_ind < 0:
                                game_ind = len(available_games) -1

                        bo = games[available_games[game_ind]]
                    except:
                        print("[ERROR] Invalid Game Recieved from Spectator")

                    sendData = pickle.dumps(bo)
                    conn.sendall(sendData)

            except Exception as e:
                print(e)

        print("[DISCONNECT] Spectator left game", game)
        specs -= 1
        conn.close()


while True:
    read_specs()
    if connections < MAX_CONNECTIONS:
        conn, addr = s.accept()
        spec = False
        g = -1
        print("[CONNECT] New connection")

        for game in games.keys():
            if games[game].ready == False:
                g=game

        games[g] = Board(8,8)
        if g == -1:
            try:
                g = list(games.keys())[-1]+1
            except:
                g = 0

        print("[DATA] Number of Connections:", connections+1)
        print("[DATA] Number of Games:", len(games))

        start_new_thread(threaded_client, (conn,g,spec))
