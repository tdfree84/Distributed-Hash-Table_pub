#!/usr/bin/python3
from socket import *
import sys
import os
import time
import threading
import random
from net_functions import *
from hash_functions import *
from peerProfile import *

def handlePeer(peerInfo):
    ''' handlePeer receives commands from a client sending requests. '''

    #handle a new client that connects
    print("I have connected with someone.")
    peerConn, peerAddr = peerInfo
    conMsg = recvAll(peerConn, 3)
    print(conMsg)
    peerIP, peerPort = recvAddress(peerConn)
    print(peerIP + ":" + str(peerPort))
    if getHashIndex( (peerIP, peerPort) ) > myKeySpaceRange[0] and getHashIndex( (peerIP, peerPort) ) < myKeySpaceRange[1]:
        #sending them a T if we own they space they want
        peerConn.send('T'.encode())

        #send the address of our successor

        #send the number of items from their hash
        #to the hash of the successor

        #for number of items, send [key][valSize][val] to peer

        #receive a T from the client to say everything was received

        #once done, we no longer own that keyspace, so update
        #our keyspace ranges
    else:
        #send this if we don't own the space they want
        peerConn.send('N'.encode())

def waitForPeerConnections(listener):
    ''' waitForPeerConnections listens for other peers to connect to us and spawns off a new thread for each peer that connects. '''

    while running:
        peerInfo = listener.accept()
        threading.Thread(target=handlePeer, args = (peerInfo,), daemon=True).start()

listener = socket(AF_INET, SOCK_STREAM)
listener.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
listener.bind(('', 0))
listener.listen(32)
port = listener.getsockname()[1]
print("I am: " + getLocalIPAddress() + ":" + str(port))

running = True

#to populate fingerTable, after owns is implemented, we can call
#owns on the offsets we find in the key range to find peers to communicate with
#and populate the fingerTable automatically
fingerTable = {}
keySpaceRanges = 2**160/5
#get random number in keyRange for offset
randKeyRange = random.randint(0, keySpaceRanges)
#all the keyspace we own
myKeySpaceRange = []

# Seed client is len == 1
if len(sys.argv) == 1:
    #set up our own thread to start listening for clients
    threading.Thread(target=waitForPeerConnections, args = (listener,), daemon=True).start()
    addr = getLocalIPAddress() + ":" + port
    fingerTable[addr] = 2**160
    myKeySpaceRange[0] = 0
    myKeySpaceRange[1] = 2**160

    userInput = input("Command?")
    while userInput != "disconnect":
        print("Running")
        print("--MENU--")

        

        userInput = input("Command?")
    

    print("This is a the seed client")
    #this will be for the initial person connecting

# Connecting client passes arguments of ip and port
elif len(sys.argv) == 3:
    #this is for any peer trying to connect to another peer
    #set up our own thread to start listening for clients
    threading.Thread(target=waitForPeerConnections, args = (listener,), daemon=True).start()

    # Continue connecting to peer the user chose
    peerIP = sys.argv[1]
    peerPort = int(sys.argv[2])
    peerConn = socket(AF_INET, SOCK_STREAM)
    peerConn.connect( (peerIP, peerPort) )

    #send the client we connected to our connection protocol
    peerConn.send("CON".encode())
    peerAddress = (getLocalIPAddress(), port)
    sendAddress(peerConn, peerAddress)

    tf = recvAll(peerConn, 1)

    userInput = input("Command?")

    while userInput != "disconnect":
        print("Running")

        userInput = input("Command?")
else:
    print("What you doing?")







