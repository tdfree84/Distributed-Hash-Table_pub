from socket import *
from tfbvDHT.net_functions import *
from tfbvDHT.hash_functions import getHash

# Class to interact with DHT via network protocol
class DHTInterface:
    def __init__(self):
        self.conn = None
        self.peerIP = None
        self.peerPort = None

    # Make sure key is sendable
    def prepKey(self, key):
        if type(key) is str:
            return getHash(key.encode())
        else:
            return getHash(key)

    # Read ip/port from local file named IPPORT.txt
    def read_and_set_connection(self, file_name):
        IPPORT = None
        with open(file_name, 'r') as f:
            line = f.readline()
            try:
                IPPORT = line.split(':')
            except:
                raise("IPPORT file was not proper.")
        self.set_connection(IPPORT[0], int(IPPORT[1]))

    # Set connection
    def set_connection(self, peerIP, peerPort):
        self.conn = socket(AF_INET, SOCK_STREAM)
        try:
            self.conn.connect((peerIP, int(peerPort)))
            print("Connected")
        except:
            close_connection()
            raise("Could not connect to",peerIP,peerPort)

    # Close connection
    def close_connection(self):
        try:
            self.conn.close()
        except:
            raise("Couldn't close connection. Hard reset")
        self.conn = None
        self.peerIP = None
        self.peerPort = None

    # Inserting value into DHT
    def insert(self, key, value):
        if self.conn is None:
            raise("Not connected to a peer")
        self.conn.send("INS".encode())
        sendKey(self.conn, getHash(key))
        response1 = recvAll(self.conn, 1)
        sendVal(value)
        response2 = recvAll(self.conn, 1)

    # Removing value from DHT
    def remove(self, key):
        if self.conn is None:
            raise("Not connected to a peer")
        self.conn.send("REM".encode())
        sendKey(self.conn, getHash(key))
        response1 = recvAll(self.conn, 1)

    # Getting value from the DHT by key
    def get(self, key):
        if self.conn is None:
            raise("Not connected to a peer")
        self.conn.send("GET".encode())
        sendKey(self.conn, getHash(key))
        response1 = recvAll(self.conn, 1)
        data = None
        if response1.decode() == 'T':
            data = recvVal(self.conn)

    # Checking for existence of a key
    def exists(self, key):
        if self.conn is None:
            raise("Not connected to a peer")
        self.conn.send("EXI".encode())

        key_to_send = self.prepKey(key)

        sendKey(self.conn, key_to_send)
        response1 = recvAll(self.conn, 1)
        return response1.decode()
