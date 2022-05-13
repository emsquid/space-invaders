import socket
import pickle
from _thread import start_new_thread
from src.variables import PORT
from src.engines import MultiEngine


def check_connection() -> bool:
    """check if we can connect to internet"""
    try:
        # create a socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        # connect to the server
        s.connect(("1.1.1.1", 53))
        s.close()
        return True
    except:
        return False


class Server:
    def __init__(self) -> None:
        """initialize the server"""
        self.socket = None
        self.ip = ""
        self.port = PORT
        self.running = False

        self.games = {}
        self.idCount = 0

    def find_ip(self) -> bool:
        """find an ip address"""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        try:
            s.connect(("8.8.8.8", 1))
            self.ip = s.getsockname()[0]
        except:
            self.ip = "127.0.0.1"
        finally:
            s.close()

    def start(self) -> bool:
        """start the server, return True if successful"""
        try:
            # create a socket and find an ip
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.find_ip()
            # bind the socket to the ip and port and connect
            self.socket.bind((self.ip, self.port))
            self.socket.listen()
            return True
        except:
            return False

    def close(self) -> None:
        """close the server"""
        # set running to false to stop the server
        if self.running:
            self.running = False
            try:
                # create a temporary socket to make sure the server stop running
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((self.ip, self.port))
                # close the socket definitely
                self.socket.close()
            except:
                pass

    def run(self) -> None:
        """run the server and handle client connections"""
        self.running = True

        while self.running:
            try:
                conn, addr = self.socket.accept()
                assert self.running
            except:
                break
            else:
                # find a game to join, if none available create a new game
                gameId = self.find_game()
                if gameId is None:
                    playerId = 0
                    # create a new game
                    gameId = self.idCount
                    self.idCount += 1

                    self.games[gameId] = MultiEngine()
                else:
                    playerId = 1
                    # join an existing game
                    self.games[gameId].ready = True
                    self.games[gameId].player_count += 1

                # start a new thread for the client
                start_new_thread(self.threaded_client, (conn, playerId, gameId))

    def threaded_client(self, conn: socket.socket, playerId: int, gameId: int) -> None:
        """handle a client by receiving and sending game data"""
        # send id to client
        conn.send(str.encode(str(playerId)))
        # receive name from client
        name, style = conn.recv(1024).decode().split("|")
        self.games[gameId].player_names[playerId] = name
        self.games[gameId].players[playerId].change_style(style)
        # send game data to client every frame
        while self.running:
            try:
                data = conn.recv(512).decode()
                game = self.games.get(gameId, None)  # type: MultiEngine

                if not data or not game:
                    break
                # execute the received commands
                for req in data.split("|"):
                    if req.startswith("direction"):
                        data = req.split(":")[1]
                        direction = data
                        game.change_direction(playerId, direction)
                    elif req.startswith("shoot"):
                        game.shoot_laser(playerId)
                    # only update if player is alone or if he is id 0
                    elif req.startswith("update") and (
                        game.player_count == 1 or playerId == 0
                    ):
                        data = req.split(":")[1]
                        dt = int(data)
                        game.update(dt)

                game_data = game.get_data(playerId)
                # send game data to client
                conn.sendall(pickle.dumps(game_data))
            except:
                break

        # quit game and close client connection
        if gameId in self.games.keys():
            self.games[gameId].player_count -= 1
            if self.games[gameId].player_count == 0:
                del self.games[gameId]
        conn.close()

    def find_game(self) -> int:
        """find an available game, return None if no games are available"""
        for gameId in self.games.keys():
            if not self.games[gameId].ready:
                return gameId
        return None


class Client:
    def __init__(self) -> None:
        """initialize the client"""
        self.socket = None
        self.ip = ""
        self.port = PORT

        self.connected = False

        self.playerId = None

        self.cache = None

    def connect(self, ip: str, name: str, style: int) -> None:
        """connect to the server and send the name"""
        try:
            # create a socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.settimeout(5)
            self.ip = ip
            # connect to the server
            self.socket.connect((self.ip, self.port))
            # if we receive an id and we can send a name, we are connected
            self.playerId = int(self.socket.recv(16).decode())
            self.socket.send(str.encode(f"{name}|{style}"))
            self.connected = True
        except:
            pass

    def disconnect(self) -> None:
        """disconnect from the server"""
        if self.connected:
            self.socket.close()
            self.connected = False

    def send(self, data):
        """send and receive data from the server"""
        try:
            self.socket.send(str.encode(data))
            reply = self.socket.recv(2048)
            # try to unpickle the data, if it crashes return cached data
            try:
                reply = pickle.loads(reply)
                self.cache = reply
            except:
                reply = self.cache
            return reply
        except:
            return None
