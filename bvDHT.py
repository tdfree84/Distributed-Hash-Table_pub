#!/usr/bin/python3
from socket import *
import sys
import os
import time
import threading
import net_functions
import hash_functions

def handlePeer(peerInfo):
    #handle a new client that connects
    print("You have connected and are being handled")
    peerConn, peerAddr = peerInfo
    conMsg = peerConn.hash_functions.recvAll(peerConn, 3)
    print(conMsg)
    peerIP, peerPort = peerConn.recvAddress(peerConn)
    print(peerIP + ":" + peerPort)
    #fingerTable = {}
    #keySpaceRanges = 2**160/5

##port = 54545
listener = socket(AF_INET, SOCK_STREAM)
listener.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
listener.bind(('', 0))
listener.listen(32)
port = listener.getsockname()[1]
print("I am: " + net_functions.getLocalIPAddress() + ":" + str(port))

running = True

if len(sys.argv) == 1:
    fingerTable = {}
    keySpaceRanges = 2**160/5
    #set up our own thread to start listening for clients
    while running:
        threading.Thread(target=handlePeer, args = (listener.accept(),), daemon=True).start()
    print("This is a the seed client")
    #this will be for the initial person connecting
elif len(sys.argv) == 3:
    #this is for any peer trying to connect to another peer
    print("This is a peer connecting")
    #set up our own thread to start listening for clients
    while running:
        threading.Thread(target=handlePeer, args = (listener.accept(),), daemon=True).start()

    peerIP = sys.argv[1]
    peerPort = int(sys.argv[2])

    peerConn = socket(AF_INET, SOCK_STREAM)
    peerConn.connect( (peerIP, peerPort) )
else:
    print("What you doing?")

    #send the client we connected to our connection protocol
    peerConn.send("CON".encode())
    peerAddress = net_functions.getLocalIPAddress() + ":" + str(port)
    peerConn.hash_functions.sendAddress(peerConn, peerAddress)






