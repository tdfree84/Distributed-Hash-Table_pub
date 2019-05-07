class PeerProfile:
    '''
        Data structures:
        
        myAddress: tuple( getLocalIPAddress(), int(port) )

        minHash: int( getHashIndex((getLocalIPAddress(), int(port))) )
        maxHash: int( getHashIndex((getLocalIPAddress(), int(port))) - 1 )

        fingerTable: { key = getHashIndex((getLocalIPAddress(), int(port))) : value = str(getLocalIPAddress():port), ... }

        successor: str( getLocalIPAddress() + ":" + port )
        predecessor: str( getLocalIPAddress() + ":" + port )

    '''

    def __init__(self, _myAddr,_fingerTable, _successor, _successorTwo):
        self.fingerTable = _fingerTable
        self.successor = _successor
        self.successorTwo = _successorTwo
        self.myAddress = _myAddr
        self.locked = False

    def myAddrString(self):
        return self.myAddress[0]+":"+str(self.myAddress[1])

    def serialize(self):
        inf = ''
        inf += "address " + self.myAddrString() + "\n"

        for f in self.fingerTable:
                inf += str(f) + ": "
                inf += self.fingerTable[f] + "\n"

        inf += self.successor + "\n"
        return inf

