from hash_functions import *
from net_functions import *
from socket import *

class PeerProfile:
    '''
        Data structures:
        
        myAddress: tuple( getLocalIPAddress(), int(port) )

        fingerTable: { key = getHashIndex((getLocalIPAddress(), int(port))) : value = str(getLocalIPAddress():port), ... }

        successor: str( getLocalIPAddress() + ":" + port )
        successorTwo: str( getLocalIPAddress() + ":" + port )

    '''

    def __init__(self, _myAddr,_fingerTable, _successor, _successorTwo):
        self.fingerTable = _fingerTable
        self.successor = _successor
        self.successorTwo = _successorTwo
        self.myAddress = _myAddr
        self.locked = False

    def myAddrString(self):
        ''' Return my address in form (string: "ip:port"). '''

        return self.myAddress[0]+":"+str(self.myAddress[1])

    def serialize(self):
        ''' Return a string version of all details of the class. '''

        inf = ''
        inf += "Address: " + self.myAddrString() + "\n"

        for f in self.fingerTable:
                inf += str(f) + ": "
                inf += self.fingerTable[f] + "\n"

        inf += "Successor: " + self.successor + "\n"
        inf += "Successor2: " + self.successorTwo + "\n"
        return inf

    def updateProfile(self, trueOwner):
        '''
            Updates the finger table of the peer with more recent peers
            in the DHT. That is, it will update it's successor, successorTwo, and finger
            table. Finger table is updated by calculating a random offset
            and calculating five offsets to check. These five offsets will be added to
            the finger table.

            Note: the finger table doesn't have to have five distinct peers. One peer could
            own two of the spots checked.
        '''

        # Check successor one is still active
        myHash = getHashIndex(self.myAddress)
        _successor = trueOwner(myHash - 1) # Successor is one behind us
        print("behind us: [{}]".format(_successor))
        conn = socket(AF_INET, SOCK_STREAM)
        connIP = _successor.split(':')[0]
        connPort = int(_successor.split(':')[1])

        contacted_successor_one = False
        # Try to connect to them
        try:
            conn.connect((connIP, connPort))
            conn.send('PUL'.encode())
            res = recvAll(conn, 1)
            contacted_successor_one = res.decode() == 'T' # Mark we contacted our successor
            if res.decode() != 'T':
                raise Exception("Did not get back T from pulse")
            self.successor = connIP + ':' + str(connPort)
            conn.close()
            conn = None
        except:
            raise Exception("Could not contact successor")

        # Check successor two
        successorHash = getHashIndex((self.successor.split(':')[0], int(self.successor.split(':')[1]))) # connIP and connPort are our successors IP/port
        _successor = trueOwner(successorHash - 1) # Successor two is one behind successor 
        print("behind successor: [{}]".format(_successor))
        conn = socket(AF_INET, SOCK_STREAM)
        connIP = _successor.split(':')[0]
        connPort = int(_successor.split(':')[1])

        contacted_successor_two = False
        # Try to connect to them
        try:
            conn.connect((connIP, connPort))
            conn.send('PUL'.encode())
            res = recvAll(conn, 1)
            contacted_successor_two = res.decode() == 'T' # Mark we contacted our successor
            if res.decode() != 'T':
                raise Exception("Did not get back T from pulse")
            self.successorTwo = connIP + ':' + str(connPort)
        except:
            raise Exception("Could not contact successor two")


















