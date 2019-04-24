#!/usr/bin/python3
from socket import *
import sys
import os
import time
import threading

def handlePeer(listener):
    while running:
        #handle a new client that connects
        peerInfo = listener.accept()
        peerConn, peerAddr = peerInfo

port = 54545
listener = socket(AF_INET, SOCK_STREAM)
listener.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
listener.bind(('', port))
listener.listen(32)

#set up our own thread to start listening for clients

if len(sys.argv) == 1:
    fingerTable = {}
    keySpaceRanges = 2**160/5
    threading.Thread(target=handlePeer, args = (listener,), daemon=True).start()
    print("This is a the seed client")
    #this will be for the initial person connecting
elif len(sys.argv) == 3:
    #this is for any peer trying to connect to another peer
    print("This is a peer connecting")
    peerIP = sys.argv[1]
    peerPort = int(sys.argv[2])

    peerConn = socket(AF_INET, SOCK_STREAM)
    peerConn.connect( (peerIP, peerPort) )
else:
    print("What you doing?")










