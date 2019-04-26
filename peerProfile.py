class PeerProfile:
    '''
        Data structures:
        
        myAddress: tuple( getLocalIPAddress(), int(port) )

        minHash: int( getHashIndex((getLocalIPAddress(), int(port))) )
        maxHash: int( getHashIndex((getLocalIPAddress(), int(port))) - 1 )

        fingerTable: { key = getHashIndex((getLocalIPAddress(), int(port))) : value = str(getLocalIPAddress():port), ... }

    '''

    def __init__(self, _myAddr, _minHash, _maxHash, _fingerTable, _successor, _predecessor):
        self.minHash = _minHash
        self.maxHash = _maxHash
        self.fingerTable = _fingerTable
        self.successor = _successor
        self.predecessor = _predecessor
        self.myAddress = _myAddr

    def myAddrString():
        return myAddress[0]+":"+str(myAddress[1])
