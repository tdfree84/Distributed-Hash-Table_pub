from socket import *
from tfjfbvDHT.net_functions import *
from tfjfbvDHT.hash_functions import getHash

# Class to interact with DHT via network protocol
class DHTInterface:
    def __init__(self, **kwargs):
        self.conn = None
        self.peerIP = None
        self.peerPort = None
        self.PEER_FILE_IP_PORT = None

        passed_keys = kwargs.keys() # Grab keys passed

        # Set peer file
        if "ipport_file" in passed_keys:
            self.PEER_FILE_IP_PORT = kwargs["ipport_file"]

        # Set ip/port
        if "peerIP" in passed_keys and "peerPort" in passed_keys:
            self.peerIP = kwargs['peerIP']
            self.peerPort = kwargs['peerPort']

    # Help message
    def help(self):
        print("Available methods:")
        methods = [
            "get(key)",
            "insert(key, value)",
            "remove(key)",
            "exists(key)",
            "owns(key)",
        ]

    # Make sure key is sendable
    def prepKey(self, key):
        if type(key) is str:
            return getHash(key.encode())
        else:
            return getHash(key)

    # Make sure value is sendable
    def prepVal(self, val):
        if type(val) is str:
            return val.encode()
        else:
            return val

    # Read ip/port from local file
    def read_and_set_connection(self, file_name):
        '''
            Sets connection to already known peerIp and peerPort,
            or reads from provided file name to get
            a connection.
            Calls set_connection to set the connection.
        '''
        # If file has already been read
        # set connection with known IP and Port
        if self.peerIP is not None and self.peerPort is not None:
            self.set_connection(self.peerIP, self.peerPort)
            return

        # Need to read from file
        IPPORT = None
        try:
            with open(file_name, 'r') as f:
                line = f.readline()
                try:
                    IPPORT = line.split(':')
                except:
                    raise Exception("IPPORT file was not proper.")
        except:
            raise Exception("IPPORT file DNE")
        self.peerIP = IPPORT[0]
        self.peerPort = IPPORT[1]
        self.set_connection(IPPORT[0], int(IPPORT[1]))

    # Set connection
    def set_connection(self, peerIP, peerPort):
        '''
            Sets the self.conn to a connection
            to parameters peerIP and peerPort.
        '''
        if self.conn is not None:
            self.close_connection()

        self.conn = socket(AF_INET, SOCK_STREAM)
        self.peerIP = peerIP
        self.peerPort = peerPort
        try:
            self.conn.connect((peerIP, int(peerPort)))
            #print("Connected")
        except:
            self.close_connection()
            raise BaseException("Could not connect to",peerIP,peerPort)

    # Find who we are supposed to be connected to and connect to them
    def set_true_connection(self, key):
        '''
            Obtains the true owner to a key
            passed. A connection will then be 
            set to that owner.
        '''
        TO = self.trueOwner(key).split(':')
        self.set_connection(TO[0], TO[1])

    # Close connection
    def close_connection(self):
        '''
            Closes the connection and sets the conn
            object to None.
        '''
        if self.conn is not None:
            try:
                self.conn.close()
            except:
                print("Couldn't close connection. Hard reset")
        self.conn = None

    # Inserting value into DHT
    def insert(self, key, value):
        self.read_and_set_connection(self.PEER_FILE_IP_PORT)
        self.set_true_connection(key)

        if self.conn is None:
            raise BaseException("Not connected to a peer")
        self.conn.send("INS".encode())
        sendKey(self.conn, self.prepKey(key))

        response1 = recvAll(self.conn, 1)
        if response1.decode() == 'F':
            return response1.decode()

        sendVal(self.conn, self.prepVal(value))
    
        response2 = recvAll(self.conn, 1)
        return response2.decode()

    # Removing value from DHT
    def remove(self, key):
        self.read_and_set_connection(self.PEER_FILE_IP_PORT)
        self.set_true_connection(key)

        if self.conn is None:
            raise BaseException("Not connected to a peer")
        self.conn.send("REM".encode())
        sendKey(self.conn, self.prepKey(key))
        response1 = recvAll(self.conn, 1)
        return response1.decode()

    # Getting value from the DHT by key
    def get(self, key):
        self.read_and_set_connection(self.PEER_FILE_IP_PORT)
        self.set_true_connection(key)

        if self.conn is None:
            raise BaseException("Not connected to a peer")
        self.conn.send("GET".encode())
        sendKey(self.conn, self.prepKey(key))
        response1 = recvAll(self.conn, 1)
        data = None
        if response1.decode() == 'T':
            data = recvVal(self.conn)
        return (response1.decode(), data)

    # Checking for existence of a key
    def exists(self, key):
        self.read_and_set_connection(self.PEER_FILE_IP_PORT)
        self.set_true_connection(key)

        if self.conn is None:
            raise BaseException("Not connected to a peer")
        self.conn.send("EXI".encode())

        key_to_send = self.prepKey(key)

        sendKey(self.conn, key_to_send)
        response1 = recvAll(self.conn, 1)
        return response1.decode()

    # Finding true owner
    def trueOwner(self, key):
        candidate = self.owns(key) # First candidate to compare to
        temp = candidate
        returned_peer = ''
        while candidate != returned_peer:
            candidate = temp
            _conn = socket(AF_INET, SOCK_STREAM)
            connIP = candidate.split(':')[0]
            connPort = int(candidate.split(':')[1])

            _conn.connect((connIP, connPort))
            _conn.send("OWN".encode())
            sendKey(_conn, self.prepKey(key))

            returned_peer = recvAddress(_conn)
            returned_peer = returned_peer[0] + ":" + str(returned_peer[1])
            temp = returned_peer
            _conn.close()

        return temp # If here, temp is the true owner

    # Ask for who owns the space
    def owns(self, key):
        if self.conn is None:
            self.read_and_set_connection(self.PEER_FILE_IP_PORT)
        self.conn.send("OWN".encode())

        key_to_send = self.prepKey(key)

        sendKey(self.conn, key_to_send)
        response1 = recvAddress(self.conn)
        return response1[0] +":"+ str(response1[1])

