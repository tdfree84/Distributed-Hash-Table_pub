class PeerProfile:

    def __init__(self, _myAddr, _minHash, _maxHash, _fingerTable, _successor, _predecessor):
        self.minHash = _minHash
        self.maxHash = _maxHash
        self.fingerTable = _fingerTable
        self.successor = _successor
        self.predecessor = _predecessor
        self.myAddress = _myAddr
