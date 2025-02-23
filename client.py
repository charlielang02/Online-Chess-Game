import socket
import pickle
import time

BUFFER_SIZE = 4096 * 8
TIMEOUT_SECONDS = 5

class Network:
    def __init__(self):'
        """
        Initializes the Network object, creates a socket connection to the server,
        and retrieves the initial game board state.
        """

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = "localhost"
        self.port = 5555
        self.addr = (self.host, self.port)
        self.board = self.connect()
        self.board = pickle.loads(self.board)

    def connect(self):
        """
        Establishes a connection to the server and retrieves the initial game state.
        
        :return: The response from the server containing the initial board state.
        """
        
        self.client.connect(self.addr)
        return self.client.recv(BUFFER_SIZE)

    def disconnect(self):
        """
        Closes the connection to the server.
        """
        
        self.client.close()

    def send(self, data, pick=False):
        """
        Sends data to the server and waits for a response. The data can be pickled or plain string.
        
        :param data: The data to send to the server, either as a string or an object to pickle.
        :param pick: A flag to indicate whether the data should be pickled before sending. Default is False.
        :return: The response received from the server.
        """
        
        start_time = time.time()
        while time.time() - start_time < TIMEOUT_SECONDS:
            try:
                if pick:
                    self.client.send(pickle.dumps(data))
                else:
                    self.client.send(str.encode(data))
                reply = self.client.recv(4096*8)
                try:
                    reply = pickle.loads(reply)
                    break
                except Exception as e:
                    print(e)

            except socket.error as e:
                print(e)


        return reply


