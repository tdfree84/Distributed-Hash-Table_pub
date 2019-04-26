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

menu = "--MENU--\nChoose 1 for: insert.\nChoose 2 for: remove.\nChoose 3 for: get.\nChoose 4 for: exists.\nChoose 5 for: owns.\nChoose 6 for: disconnect.\n"


####################
# Helper functions #
####################

def owns(number):
    ''' Find the closest person to the hash number requested. '''

    if number >= myProfile.minHash and number <= myProfile.maxHash:
        return myProfile.myAddress
    else:
        # Find the closest person we know to that number
        minDist = [0,2**160+1]
        for key in myProfile.fingerTable:
            if abs(key - number) < minDist[1]:
                minDist[0] = myProfile.fingerTable[key]
                minDist[1] = abs(key - number)
        return minDist[0] # Return their ip:port string
    

#################
# Peer handling #
#################

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
        #call owns on our max range +1 to find them
        ''' owns(this.maxHash+1) '''

        #send the number of items from their hash
        #to the hash of the successor-1

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
myKeySpaceRange = [0,0]
# THIS client's profile
myProfile = ''

# Seed client is len == 1
if len(sys.argv) == 1:
    #set up our own thread to start listening for clients
    print("This is a the seed client")
    threading.Thread(target=waitForPeerConnections, args = (listener,), daemon=True).start()
    addr = getLocalIPAddress() + ":" + str(port)
    fingerTable[getHashIndex((getLocalIPAddress(), int(port)))] = addr


    print(menu)
    print("My finger table is",fingerTable)
    myKeySpaceRange[0] = getHashIndex((getLocalIPAddress(), int(port))) 
    myKeySpaceRange[1] = getHashIndex((getLocalIPAddress(), int(port)))-1

    # Initializing my peer profile
    myProfile = PeerProfile((getLocalIPAdress(),int(port)),myKeySpaceRange[0],myKeySpaceRange[1],fingerTable,addr,addr)

    userInput = input("Command?")
    while userInput != "disconnect":
        print("Running")
        print(menu)


        

        userInput = input("Command?\n")
    

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
    if(tf == "T"):
        #recv all protocol messages from peer we connected to
        print(menu)
        userInput = input("Command?\n")
        while userInput != "disconnect":
            print("Running")
            print(menu)

            userInput = input("Command?\n")
    else:
        pass
        #run owns on our hash
else:
    print("What you doing?")







