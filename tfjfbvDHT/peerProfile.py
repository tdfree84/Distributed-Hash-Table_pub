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

        Successors' hashes are HIGHER than ours.
        That is, the successors are at the end of our keyspace.
        The end being from our keyspace to addresses greater than ours
        up until the next peer.

    '''

    def __init__(self, _myAddr,_fingerTable, _successor, _successorTwo):
        self.fingerTable = _fingerTable
        self.successor = _successor
        self.successorTwo = _successorTwo
        self.myAddress = _myAddr
        self.locked = False

        # Get random number [0, 2**160/5] for finger table populating
        import random
        from os import urandom
        random.seed(a=urandom(4096))
        self.offset = random.randint(0, (2**160)/5)

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
            in the DHT. 
            Finger table is updated by calculating a random offset
            and calculating five offsets to check. These five offsets will be added to
            the finger table.

            Note: the finger table doesn't have to have five distinct peers. One peer could
            own > 1 of the spots checked.
        '''

        check_index = 0
        for i in range(5):
            # Get who owns at each
            owner = trueOwner(check_index)
            print(f"Checking {check_index} and received {owner}")
            # Add to finger table if the IP is not already in values
            if owner not in self.fingerTable.values():
                self.fingerTable[check_index] = owner

            check_index += self.offset






















