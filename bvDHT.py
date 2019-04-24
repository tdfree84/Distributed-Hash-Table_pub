#!/usr/bin/python3
from socket import *
import sys
import os
import time
import threading
from net_functions import *
from hash_functions import *

def handlePeer(peerInfo):
    #handle a new client that connects
    print("I have connected with someone.")
    peerConn, peerAddr = peerInfo
    conMsg = recvAll(peerConn, 3)
    print(conMsg)
    peerIP, peerPort = recvAddress(peerConn)
    print(peerIP + ":" + peerPort)
    #fingerTable = {}
    #keySpaceRanges = 2**160/5

def waitForPeerConnections(listener):
    while running:
        peerInfo = listener.accept()
        threading.Thread(target=handlePeer, args = (peerInfo,), daemon=True).start()

##port = 54545
listener = socket(AF_INET, SOCK_STREAM)
listener.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
listener.bind(('', 0))
listener.listen(32)
port = listener.getsockname()[1]
print("I am: " + getLocalIPAddress() + ":" + str(port))

running = True

if len(sys.argv) == 1:
    fingerTable = {}
    keySpaceRanges = 2**160/5
    #set up our own thread to start listening for clients
    threading.Thread(target=waitForPeerConnections, args = (listener,), daemon=True).start()

    userInput = input("Command?")
    while userInput != "disconnect":
        print("Running")

        userInput = input("Command?")
    

    print("This is a the seed client")
    #this will be for the initial person connecting
elif len(sys.argv) == 3:
    #this is for any peer trying to connect to another peer
    #set up our own thread to start listening for clients
    threading.Thread(target=waitForPeerConnections, args = (listener,), daemon=True).start()

    # Continue connecting to peer the user chose
    peerIP = sys.argv[1]
    peerPort = int(sys.argv[2])
    peerConn = socket(AF_INET, SOCK_STREAM)
    peerConn.connect( (peerIP, peerPort) )

    userInput = input("Command?")
    while input != "disconnect":
        print("Running")

        userInput = input("Command?")
else:
    print("What you doing?")

#   #send the client we connected to our connection protocol
#   peerConn.send("CON".encode())
#   peerAddress = net_functions.getLocalIPAddress() + ":" + str(port)
#   peerConn.hash_functions.sendAddress(peerConn, peerAddress)






