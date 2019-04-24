#!/usr/bin/python3
from socket import *
import sys
import os
import time
import threading
import net_functions
import hash_functions

def handlePeer(listener):
    while running:
        #handle a new client that connects
        print("You have connected and are being handled")
        peerInfo = listener.accept()
        peerConn, peerAddr = peerInfo
        fingerTable = {}
        keySpaceRanges = 2**160/5

port = 54545
listener = socket(AF_INET, SOCK_STREAM)
listener.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
listener.bind(('', port))
listener.listen(32)

running = True

if len(sys.argv) == 1:
    fingerTable = {}
    keySpaceRanges = 2**160/5
    while running:
    #set up our own thread to start listening for clients
        threading.Thread(target=handlePeer, args = (listener,), daemon=True).start()
    print("This is a the seed client")
    #this will be for the initial person connecting
elif len(sys.argv) == 3:
    #this is for any peer trying to connect to another peer
    print("This is a peer connecting")
    #set up our own thread to start listening for clients
    threading.Thread(target=handlePeer, args = (listener,), daemon=True).start()

    peerIP = sys.argv[1]
    peerPort = int(sys.argv[2])

    peerConn = socket(AF_INET, SOCK_STREAM)
    peerConn.connect( (peerIP, peerPort) )










