from socket import *
from tfjfbvDHT.net_functions import *
from tfjfbvDHT.hash_functions import getHash

# Class to interact with DHT via network protocol
class DHTInterface:
    '''
        DHTInterface is utilized to interact with a DHT
        under the protocol set in Networks and Distributed Systems
        with Dr. Nathan Backman at Buena Vista University in Spring 2019.
        
        Initialization:
        x = DHTInterface(ipport_file='/path/to/file/example.txt')
            example.txt contains ['IP.IP.IP.IP:PORT']
        y = DHTInterface(peerIP='123.456.789.101', peerPort=12345)
        z = DHTInterface()
        z.peerIP = '987.654.321.000'
        z.peerPort = 65532
        
        With objects x, y, or z, the user can now call
        methods in DHTInterface to interact with the DHT.
        such as
        x.insert('asdf', 'fdsaasdf')
        x.get('asdf')
        x.exists('asdf')
        print(x.help())
    '''
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
        r = "Available methods:\n"
        methods = [
            "get(key)",
            "insert(key, value)",
            "remove(key)",
            "exists(key)",
            "owns(key)",
        ]
        for method in methods:
            r += '\t'+method+'\n'
        return r

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

    # Decide how to connect to a peer
    def read_and_set_connection(self, file_name):
        '''
            Decides if we connect to an already known peerIp and peerPort,
            or read from provided file name to get a connection.
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
            self.conn is useb by methods that
            contact the DHT.
            Internal methods rely on an already
            established connection to interact with the DHT.
        '''
        if self.conn is not None:
            self.close_connection()

        self.conn = socket(AF_INET, SOCK_STREAM)
        self.peerIP = peerIP
        self.peerPort = peerPort
        try:
            self.conn.connect((peerIP, int(peerPort)))
        except:
            self.close_connection()
            raise BaseException("Could not connect to",peerIP,peerPort)

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

    # Find who we are supposed to be connected to and connect to them
    def set_true_connection(self, key):
        '''
            First, set the connection to a peer.
            Obtain the true owner to a key
            passed. A connection will then be 
            set to that owner.
        '''
        self.read_and_set_connection(self.PEER_FILE_IP_PORT)

        TO = self.trueOwner(key).split(':')
        self.set_connection(TO[0], TO[1])

    # Inserting value into DHT
    def insert(self, key, value):
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

        self.close_connection()
        return response2.decode()

    # Removing value from DHT
    def remove(self, key):
        self.set_true_connection(key)

        if self.conn is None:
            raise BaseException("Not connected to a peer")
        self.conn.send("REM".encode())
        sendKey(self.conn, self.prepKey(key))
        response1 = recvAll(self.conn, 1)

        self.close_connection()
        return response1.decode()

    # Getting value from the DHT by key
    def get(self, key):
        self.set_true_connection(key)

        if self.conn is None:
            raise BaseException("Not connected to a peer")
        self.conn.send("GET".encode())
        sendKey(self.conn, self.prepKey(key))
        response1 = recvAll(self.conn, 1)
        data = None
        if response1.decode() == 'T':
            data = recvVal(self.conn)
        
        self.close_connection()
        return (response1.decode(), data)

    # Checking for existence of a key
    def exists(self, key):
        self.set_true_connection(key)

        if self.conn is None:
            raise BaseException("Not connected to a peer")
        self.conn.send("EXI".encode())

        key_to_send = self.prepKey(key)

        sendKey(self.conn, key_to_send)
        response1 = recvAll(self.conn, 1)

        self.close_connection()
        return response1.decode()

    # Ask for who owns the space
    def owns(self, key):
        '''
            In this interface with the DHT,
            an owns request means to obtain the
            TRUE owner of a key. This is not the DHT 
            protocol, a true owner is returned here.
            This is obtained by setting the true connection
            to the key passed.
        '''
        self.set_true_connection(key)

        self.close_connection()
        return self.peerIP + ':' + str(self.peerPort)

    # Finding true owner
    def trueOwner(self, key):
        '''
            Algorithm to obtain the true owner of
            a key. It is necessary for a DHT interface
            to interact with a true owner of a key
            because they are the only ones who can
            interact with the real data.
            Why is this needed here?
            Because a peer in the DHT is not responsible
            for delegating work.
            A peer in the DHT is only responsible for the
            data they own. So we need to interact with who really
            owns the file.
        '''
        if self.conn is None:
            raise Exception("Not connected to a peer.")
        # Contact who we know right now with an OWNS query
        self.conn.send("OWN".encode())
        key_to_send = self.prepKey(key)
        sendKey(self.conn, key_to_send)
        response1 = recvAddress(self.conn)
        # Obtain the first candidate to compare to
        candidate = response1[0] +":"+ str(response1[1])

        temp = candidate # Temp is needed as a third variable in the while loop
        returned_peer = ''
        # Algorithm that searches for the true owner of data
        # While who we ask, is not who is returned,
        # query the candidate for who owns the data
        while candidate != returned_peer:
            candidate = temp # Temp is next person to contact
            _conn = socket(AF_INET, SOCK_STREAM)
            connIP = candidate.split(':')[0]
            connPort = int(candidate.split(':')[1])

            # Send an owns query to the candidate
            _conn.connect((connIP, connPort))
            _conn.send("OWN".encode())
            sendKey(_conn, self.prepKey(key))

            returned_peer = recvAddress(_conn)
            returned_peer = returned_peer[0] + ":" + str(returned_peer[1])
            # Reset temp to who we received
            temp = returned_peer
            _conn.close()

        return temp # If here, temp is the true owner
