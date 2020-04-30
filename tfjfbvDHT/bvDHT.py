'''
    The following Distributed Hash Table code was constructed in joint between Jack Fordyce and Tyler Freese.
'''



#!/usr/bin/python3
from socket import *
import sys
import os
import time
import threading
import random
import hashlib
from net_functions import *
from hash_functions import *
from peerProfile import PeerProfile
from time import sleep
from os import path

menu = "--MENU--\nChoose 1 for: insert.\nChoose 2 for: remove.\nChoose 3 for: get.\nChoose 4 for: exists.\nChoose 5 for: owns.\nChoose 6 for: disconnect.\nChoose 7 for: finger table.\nChoose 8 for: update peer profile.\n"

#######################
###  DHT functions  ###
#######################
''' The following functions carry out DHT methods. 

    The functions are as follows in this order:
        trueOwner
        owns
        request_owns
        insertFile
        getFile
        getExists
        removeKey
        doDisconnect
'''

def trueOwner(number):
    ''' Searches the DHT looking for the REAL owner of a hash.
        With certainty, the result of this function IS the owner. 
        Successors' hashes are HIGHER than ours.
        That is, the successors are at the end of our keyspace.
        The end being from our keyspace to addresses greater than ours
        up until the next peer.
        
        param: hash (int)
        return: owner (string of form "ip:port")
    '''

    candidate = owns(number) # First candidate to compare to
    temp = candidate
    returned_peer = ''
    while candidate != returned_peer:
        candidate = temp
        conn = socket(AF_INET, SOCK_STREAM)
        connIP = candidate.split(':')[0]
        connPort = int(candidate.split(':')[1])

        conn.connect((connIP, connPort))
        conn.send("OWN".encode())
        sendKey(conn, number)

        returned_peer = recvAddress(conn)
        returned_peer = returned_peer[0] + ":" + str(returned_peer[1])
        temp = returned_peer
        conn.close()

    return temp # If here, temp is the true owner

def owns(number):
    ''' Find the closest person to the hash number requested. 
        This is only who THIS person knows. 
        
        param: hash (int)
        return: owner (string of form "ip:port")
    ''' 

    myHash = getHashIndex(myProfile.myAddress)
    
    s = myProfile.successor
    s = s.split(":")
    succHash = getHashIndex((s[0], int(s[1])))

    hashes = list(myProfile.fingerTable.keys())
    hashes.sort(reverse=True)
    if number < myHash and number >= succHash:
        hashes.remove(myHash)   

    #looking through reverse ordered hash table to see who the first person that is bigger than number is
    #if it is us, return our address, if not, establish connection, pulse, if successful, return that user
    for i in range(len(hashes)):
        if number >= hashes[i]:
            #Establish connection to person we find
            if myProfile.fingerTable[hashes[i]] == myProfile.myAddrString():
                return myProfile.myAddrString()

            conn = socket(AF_INET, SOCK_STREAM)
            connIPort = myProfile.fingerTable[hashes[i]].split(":")
            connIP = connIPort[0]
            connPort = int(connIPort[1])
            try:
                conn.connect((connIP, connPort))
                conn.send("PUL".encode())
            except:
                conn.close()
                
                if myProfile.fingerTable[hashes[i]] == myProfile.successor:
                    #initiate protocol to get new second successor 
                    myProfile.successor = myProfile.successorTwo
                    conn = socket(AF_INET, SOCK_STREAM)
                    connIPort = myProfile.successor.split(":")
                    connIP = connIPort[0]
                    connPort = int(connIPort[1])

                    #send ABD protocol to second successor
                    conn.connect((connIP, connPort))
                    conn.send("ABD".encode())
                    secondSuc = recvAddress(conn)
                    print(f"client in trouble received: {secondSuc}")
                    myProfile.successorTwo = secondSuc[0] + ":" + str(secondSuc[1])
                    conn.close()

                del myProfile.fingerTable[hashes[i]]
                return owns(number)

            t = recvAll(conn, 1)
            t = t.decode()
            if t == "T":
                conn.close()
                return myProfile.fingerTable[hashes[i]]

            conn.close()

    #if no one is found that owns that space, return the largest person in the table as they 
    #would own everything from 0 to the lowest users hash
    return myProfile.fingerTable[hashes[0]]

def request_owns():
    ''' Search for the owner of a hash. '''

    k = input("Enter a key: ")
    hashed_key = int.from_bytes(hashlib.sha1(k.encode()).digest(), byteorder="big")
    print(trueOwner(hashed_key))

def insertFile():
    ''' Inserts file into the DHT. '''


    #take info for file to store
    keyName = input("What is the name of what you want to store? ")
    value = input("What exactly do you want to store? ")
    hashed_key = int.from_bytes(hashlib.sha1(keyName.encode()).digest(), byteorder="big")

    #location who owns this hash key and connect to them
    whoisit = trueOwner(hashed_key)
    ins = whoisit.split(":")
    insIP = ins[0]
    insPort = ins[1]
    insConn = socket(AF_INET, SOCK_STREAM)
    insConn.connect( (insIP, int(insPort)) )

    #Tell them we want to insert
    insConn.send("INS".encode())

    #Send peer key of our data
    sendKey(insConn, int(hashed_key))
    #Wait for them to respond
    tf = recvAll(insConn, 1)
    tf = tf.decode()

    print("Receiving back from peer:",str(tf))
    if tf == "T":
        pass
    else:
        print("Something went wrong with your destination storage.")
        insConn.close()
        return

    #Send data if we can
    sendVal(insConn, value.encode())
    #Wait for them to respond
    tf = recvAll(insConn, 1)
    tf = tf.decode()
    if tf == "T":
        print("all went good.")
    else:
        print("Something went wrong with your destination storage.")
        insConn.close()
        return

    insConn.close()
    return

def getFile():
    ''' Retrieves data in the DHT. '''

    # Collect what the user wants from the hash table
    what = input("What is the name of the thing you want? ")
    hashed_key = int.from_bytes(hashlib.sha1(what.encode()).digest(), byteorder="big")

    #determine ownership of hashed key
    whoisit = trueOwner(hashed_key)
    print("This person owns it:",whoisit)
    get = whoisit.split(":")
    getIP = get[0]
    getPort = get[1]
    getConn = socket(AF_INET, SOCK_STREAM)
    getConn.connect( (getIP, int(getPort)) )

    #send get request to user who says they own
    getConn.send("GET".encode())
    sendKey(getConn, hashed_key)


    # Receive peer response #
    tf = recvAll(getConn, 1)
    tf = tf.decode()
    if tf == "T":
        data = recvVal(getConn)
        with open("repo/"+str(hashed_key), 'wb') as f:
            f.write(data)
        print("Received the data.")
    elif tf == "F":
        print("Data not found")
    elif tf == "N":
        print("Peer doesn't own this space")
        #rerun owns on the key
    else:
        print("IDK what happened.")

    getConn.close()

    return

def getExists():
    ''' Checks if a file exists in the DHT. '''


    # Collect what the user wants from the hash table
    what = input("What is the name of the thing you want to check for? ")
    hashed_key = int.from_bytes(hashlib.sha1(what.encode()).digest(), byteorder="big")

    #determine ownership
    whoisit = trueOwner(hashed_key)
    print("This person owns it:",whoisit)
    exi = whoisit.split(":")
    exiIP = exi[0]
    exiPort = exi[1]
    exiConn = socket(AF_INET, SOCK_STREAM)
    exiConn.connect( (exiIP, int(exiPort)) )

    #send exist request 
    exiConn.send("EXI".encode())
    sendKey(exiConn, hashed_key)

    # Receive peer response #
    tf = recvAll(exiConn, 1)
    tf = tf.decode()
    if tf == "T":
        print("Got a T, they have it")
    elif tf == "F":
        print("Data not found")
    elif tf == "N":
        print("Peer doesn't own this space")
        #rerun owns on the key
    else:
        print("IDK what happened.")

    exiConn.close()

    return

def removeKey():
    ''' Removes an item from the distributed hash table. '''


    # Collect what the user wants from the hash table
    what = input("What is the name of the thing you want to delete? ")
    hashed_key = int.from_bytes(hashlib.sha1(what.encode()).digest(), byteorder="big")

    #determine ownership
    whoisit = trueOwner(hashed_key)
    print("This person owns it:",whoisit)
    rem = whoisit.split(":")
    remIP = rem[0]
    remPort = rem[1]
    remConn = socket(AF_INET, SOCK_STREAM)
    remConn.connect( (remIP, int(remPort)) )

    #send remove request
    remConn.send("REM".encode())
    sendKey(remConn, hashed_key)

    # Receive peer response #
    tf = recvAll(remConn, 1)
    tf = tf.decode()
    if tf == "T":
        print("Got a T, they removed it")
    elif tf == "F":
        print("Data not found")
    elif tf == "N":
        print("Peer doesn't own this space")
        #rerun owns on the key
    else:
        print("IDK what happened.")

    remConn.close()

    return

def doDisconnect():
    ''' Disconncet from the DHT.
        Assures your successor is willing to accept your data.'''

    #hash index of our address -1
    k = getHashIndex(myProfile.myAddress)-1

    #determine ownership, aka predecessor
    whoisit = trueOwner(k)
    print("This person owns it:",whoisit)
    dis = whoisit.split(":")
    disIP = dis[0]
    disPort = dis[1]
    disConn = socket(AF_INET, SOCK_STREAM)
    disConn.connect( (disIP, int(disPort)) )

    #send disconnect request
    disConn.send("DIS".encode())
    sendAddress(disConn, myProfile.myAddress)

    # Receive peer response #
    tf = recvAll(disConn, 1)
    tf = tf.decode()
    if tf == "T":
        print("Got a T, they are ready for us to disconnect")
    elif tf == "N":
        print("Peer doesn't own this space")
        return
    #rerun owns on the key
    else:
        print("IDK what happened.")
        return

    #get our successor to send to predecessor
    s = myProfile.successor.split(':')
    sendAddress(disConn, (s[0], int(s[1]))) # Send S1
    st = myProfile.successorTwo.split(':')
    sendAddress(disConn, (st[0], int(st[1]))) # Send S2

    successorIP = myProfile.successor.split(':')[0]
    successorPort = int(myProfile.successor.split(':')[1])


    #get file names from repo
    fNameList = os.listdir('repo')
    listToSend = []
    for n in fNameList:
        nInt = int(n)
        #check if filename is in between us and successor
        if nInt < getHashIndex((successorIP, int(successorPort))) and nInt >= getHashIndex(myProfile.myAddress):
            listToSend.append(n)

    #send number of viable files
    sendInt(disConn, len(listToSend))

    #for number of items, send [key][valSize][val] to peer
    print("Sending data...")
    for n in listToSend:
        f = open('repo/' + n, 'rb')
        fBytes = f.read()
        sendKey(disConn, int(n))
        sendVal(disConn, fBytes) 
        f.close()

    # Receive peer response #
    tf = recvAll(disConn, 1)
    tf = tf.decode()
    if tf == "T":
        print("Got a T, they accepted everything")
    else:
        print("IDK what happened.")
        return

    # Fully disconnect
    print("bye")
    sys.exit(0)


#################
# Peer handling #
#################

def handlePeer(peerInfo):
    ''' 
        handlePeer receives commands from a client sending requests.
        This is the function that responds to outside (peer) commands. 
        
        param: connection object retrieved from listener.accept
    '''

    #handle a new client that connects
    peerConn, peerAddr = peerInfo

    conMsg = recvAll(peerConn, 3)
    conMsg = conMsg.decode()
    if conMsg!='' and conMsg!='\n' and conMsg != ' ':
        print("Incoming message: " + conMsg)
    if conMsg == "CON":
        #####################
        #CONNECTION PROTOCOL#
        #####################
        while myProfile.locked:
            sleep(1)
            pass

        #set lock to true
        myProfile.locked = True

        #receive address of person trying to connect
        peerIP, peerPort = recvAddress(peerConn)
        print("THIS PERSON IS CONNECTING: " + peerIP + ":" + str(peerPort))

        #calculate our hash and peer's hash
        peerHash = getHashIndex((peerIP, peerPort))
        myHash = getHashIndex(myProfile.myAddress)

        #get our successor in order to send to person connecting
        successor = myProfile.successor.split(":")
        successorIP = successor[0]
        successorPort = int(successor[1])
        successorHash = getHashIndex((successorIP, successorPort))
        
        #get successor 2
        successorTwo = myProfile.successorTwo.split(":")
        successorTwoIP = successorTwo[0]
        successorTwoPort = int(successorTwo[1])
        successorTwoHash = getHashIndex((successorTwoIP, successorTwoPort))


        #if we own the peer's hash, continue with protocol, else, send N and skip
        if trueOwner(peerHash) == myProfile.myAddrString():
            peerConn.send("T".encode())
        else:
            peerConn.send("N".encode())
            myProfile.locked = False
            return

        #update our fingertable by adding peer who just connected to us
        fingerTable[getHashIndex((peerIP, int(peerPort)))] = peerIP + ":" + str(peerPort)

        #send the address of our successor
        sendAddress(peerConn, (successorIP, successorPort))

        #send address of second successor
        sendAddress(peerConn, (successorTwoIP, successorTwoPort))

        #get file names from repo
        fNameList = os.listdir('repo')
        listToSend = []
        for n in fNameList:
            nInt = int(n)
            if nInt < getHashIndex((successorIP, int(successorPort))) and nInt > getHashIndex((peerIP, int(peerPort))):
                listToSend.append(n)

        #send number of files
        sendInt(peerConn, len(listToSend))

        #for number of items, send [key][valSize][val] to peer
        for n in listToSend:
            f = open('repo/' + n, 'rb')
            fBytes = f.read()
            sendKey(peerConn, int(n))
            sendVal(peerConn, fBytes) 
            f.close()


        #receive a T from the client to say everything was received
        tf = recvAll(peerConn, 1)
        tf = tf.decode()
        if tf == 'T':
            #set successor to person who just connected to us
            #they are now our new successor
            #update second successor to old original successor
            myProfile.successorTwo = myProfile.successor
            myProfile.successor = peerIP + ":" + str(peerPort)

        myProfile.locked = False

    elif conMsg == "DIS":
        #####################
        #DISCONNECT PROTOCOL#
        #####################
        while myProfile.locked:
            sleep(1)
            pass

        #set lock
        myProfile.locked = True

        peerAddr = recvAddress(peerConn)
        peerAddrStr = peerAddr[0] + ":" + str(peerAddr[1])
        if trueOwner(getHashIndex((peerAddr[0], peerAddr[1]))-1) == myProfile.myAddrString():

            #sending them a T if we own they space they want
            peerConn.send('T'.encode())

            #receive address of our new successor
            successor = recvAddress(peerConn)
            successorIP = successor[0]
            successorPort = successor[1]

            #receive successor 2
            successorTwo = recvAddress(peerConn)
            successorTwoIP = successorTwo[0]
            successorTwoPort = successorTwo[1]
            successorTwoHash = getHashIndex((successorTwoIP, successorTwoPort))

            #receive amount of files they want to send
            numItems = recvInt(peerConn)

            #for number of files, receive key and value and write it to file
            print("Receiving data...")
            for n in range(numItems):
                try:
                    k = recvKey(peerConn)
                    data = recvVal(peerConn)
                    f = open('repo/' + str(k), 'wb')
                    f.write(data)
                    f.close()
                except:
                    print("Failed to write some data when peer was disconnecting")

            #send them a T, delete them from finger table and close connection
            peerConn.send("T".encode())
            del fingerTable[getHashIndex(peerAddr)]
            peerConn.close()

            #update our info
            myProfile.successor = successorIP + ":" + str(successorPort)
            myProfile.successorTwo = successorTwoIP + ":" + str(successorTwoPort)

            fingerTable[getHashIndex((successorIP, int(successorPort)))] = successorIP + ":" + str(successorPort)

            fingerTable[getHashIndex((successorTwoIP, int(successorTwoPort)))] = successorTwoIP + ":" + str(successorTwoPort)

            myProfile.locked = False

            #return 

        else:
            #send this if we don't own the space they want
            peerConn.send("N".encode())
            myProfile.locked = False



    elif conMsg == "INS":
        #################
        #INSERT PROTOCOL#
        #################
        while myProfile.locked:
            pass

        fileName = recvKey(peerConn) # Integer representation of file name (hash)

        successor = myProfile.successor.split(":")
        successorIP = successor[0]
        successorPort = successor[1]

        successorHash = getHashIndex((successorIP, int(successorPort))) # Not used
        myHash = getHashIndex(myProfile.myAddress) # Not used

        #if we own the space, send positive confirmation
        #else, send N and skip
        if trueOwner(fileName) == myProfile.myAddrString():
            peerConn.send("T".encode())
        else:
            peerConn.send("N".encode())
            return


        #receive data, write it to file, send F
        #if something fails, send F
        try:
            print("Inserting file...")
            fileContent = recvVal(peerConn)
            f = open('repo/' + str(fileName), 'wb')
            f.write(fileContent)
            f.close()
            peerConn.send("T".encode())
        except:
            peerConn.send("F".encode())

    elif conMsg == "OWN":
        ##OWNS PROTOCOL##

        #return person who we know to be closest in our finger table
        key = recvKey(peerConn)
        owner = owns(key)

        ownerList = owner.split(":")
        ownerIP = ownerList[0]
        ownerPort = int(ownerList[1])
        sendAddress(peerConn, (ownerIP, ownerPort))

    elif conMsg == "GET":
        ##GET PROTOCOL##
        while myProfile.locked:
            pass

        key = recvKey(peerConn)

        #if we own the space and we can find a corresponding file,
        #send it, else send F
        #if we don't own, send N
        if trueOwner(key) == myProfile.myAddrString():
            try:
                print("Sending file...")
                f = open("repo/"+str(key), "rb")
                fileToSend = f.read()
                peerConn.send("T".encode())
                sendVal(peerConn, fileToSend)
                f.close()
            except:
                peerConn.send("F".encode())
        else:
            peerConn.send("N".encode())

    elif conMsg == "EXI":
        ##EXISTS PROTOCOL##

        #receive key
        key = recvKey(peerConn)

        #if trueOwner returns us, and we can find a file with that keyname, send a T
        #if we can't find file, send F
        #if we don't own the space, send N
        if trueOwner(key) == myProfile.myAddrString():
            try:
                f=open("repo/"+str(key), "rb")
                peerConn.send("T".encode())
                f.close()
            except:
                peerConn.send("F".encode())
        else:
            peerConn.send("N".encode())

    elif conMsg == "REM":
        ##REMOVE PROTOCOL##
        while myProfile.locked:
            pass

        #receive key
        key = recvKey(peerConn)
        keyStr = str(key)

        #call true owner on Key and it it is us, proceed
        #if not, send and N
        if trueOwner(key) == myProfile.myAddrString():
            try:
                print("Removing file...")
                #try to remove data, if something fails, send an F
                f=open("repo/"+keyStr, "rb")
                os.remove("repo/"+keyStr)
                #after attempting to remove, check to see if a path with that name still exists
                if not (os.path.exists("repo/"+keyStr)):
                    peerConn.send("T".encode())
            except:
                peerConn.send("F".encode())
        else:
            peerConn.send("N".encode())

    elif conMsg == "PUL":
        #if PUL is received, send T and close connection
        peerConn.send("T".encode())
        peerConn.close()
        #return

    elif conMsg == "INF":
        #uses function in our class to put diagnostic information into a string and send to whoever requested
        fingerString = myProfile.serialize()
        sendVal(peerConn, fingerString)

    elif conMsg == "ABD":
        successor = myProfile.successor.split(':')
        print(f"abd successor:{successor}")
        successorIP = successor[0]
        successorPort = int(successor[1])
        sendAddress(peerConn, (successorIP, successorPort))

    return


def waitForPeerConnections(listener):
    ''' waitForPeerConnections listens for other peers to connect to us and spawns off a new thread for each peer that connects. 
        
        param: listener object created for peers to connect to
        '''

    while True:
        peerInfo = listener.accept()
        t1 = threading.Thread(target=handlePeer, args = (peerInfo,), daemon=True)
        t1.start()
        #t1.join() # Join = wait in C



####################################
#######                      #######
######  BEGINNING OF RUNNING  ######
#######                      #######
####################################

#set up listener for anyone trying to start the hash table
listener = socket(AF_INET, SOCK_STREAM)
listener.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
listener.bind(('', 0))
listener.listen(32)
port = listener.getsockname()[1]
print("I am: " + getLocalIPAddress() + ":" + str(port))

#initialize finger table
fingerTable = {}
keySpaceRanges = 2**160/5
#get random number in keyRange for offset
randKeyRange = random.randint(0, keySpaceRanges)
# THIS client's profile
myProfile = ''

# Ensure we have repo folder
if not path.exists('repo/'):
    os.mkdir('repo')

# Seed client is len == 1
if len(sys.argv) == 1:
    ''' Running this file as a seed client for a DHT. '''

    #set up our own thread to start listening for clients
    print("This is a seed client")
    threading.Thread(target=waitForPeerConnections, args = (listener,), daemon=True).start()
    addr = getLocalIPAddress() + ":" + str(port)
    fingerTable[getHashIndex((getLocalIPAddress(), int(port)))] = addr

    ourHash = getHashIndex((getLocalIPAddress(), int(port)))

    # Initializing my peer profile
    myProfile = PeerProfile((getLocalIPAddress(),int(port)),fingerTable,addr,addr)
    
    print(menu)
    #waiting for commands
    try:
        userInput = input("Command?\n")
    except KeyboardInterrupt:
        print("Rogue client...")
        doDisconnect()

    try:
        while True:
            if userInput == "1":
                ##INSERT##
                insertFile()

            elif userInput == "2":
                ##REMOVE##
                removeKey()

            elif userInput == "3":
                ##GET##
                getFile()

            elif userInput == "4":
                ##EXISTS##
                getExists()

            elif userInput == "5":
                ##OWNS##
                request_owns()

            elif userInput == "6":
                ##DISCONNET##
                doDisconnect()

            elif userInput == "7":
                ##DIAGNOSTICS##
                print(myProfile.serialize()) 

            elif userInput == "8":
                ##UPDATE PROFILE##
                myProfile.updateProfile(trueOwner) 

            else:
                ##BOGUS##
                print("What?")

            print(menu)
            userInput = input("Command?\n")

    except KeyboardInterrupt:
        print("Rogue client...")
        doDisconnect()

# Connecting client passes arguments of ip and port
elif len(sys.argv) == 3:
    ''' This peer is connecting to the DHT via contacting the real owner of their hash. 
        
        param1: ip
        param2: port
    '''    

    #this is for any peer trying to connect to another peer
    #set up our own thread to start listening for clients
    threading.Thread(target=waitForPeerConnections, args = (listener,), daemon=True).start()

    # Continue connecting to peer the user chose
    peerIP = sys.argv[1]
    peerPort = int(sys.argv[2])
    peerConn = socket(AF_INET, SOCK_STREAM)
    peerConn.connect( (peerIP, peerPort) )

    # setting up info for our peer profile
    # adding who we just connected to to our finger table
    myAddress = (getLocalIPAddress(), port)
    fingerTable[getHashIndex((peerIP, peerPort))] = peerIP + ":" + str(peerPort) # add peer
    myAddressString = myAddress[0] + ":" + str(myAddress[1])
    myProfile = PeerProfile((getLocalIPAddress(),int(port)),fingerTable,myAddressString,myAddressString)

    # figuring out who really owns the space where we will be inserted
    # by running true owns on our hash
    # then, connecting to that peer by sending "CON"
    myHash = getHashIndex(myAddress)
    peer = trueOwner(myHash)
    peer = peer.split(":")
    peerIP = peer[0]
    peerPort = int(peer[1])
    peerConn.close()

    peerConn = socket(AF_INET, SOCK_STREAM)
    peerConn.connect( (peerIP, peerPort) )

    #send the client we connected to our connection protocol
    peerConn.send("CON".encode())

    sendAddress(peerConn, myAddress)

    tf = recvAll(peerConn, 1)
    tf = tf.decode()

    if tf == "T":

        # Gathering info for our profile
        # Add ourselves to the finger table
        #fingerTable[getHashIndex((getLocalIPAddress(), int(port)))] = myAddressString

        # Finish out rest of connection protocol after we have the ok to continue #
        peerSuccessor1 = recvAddress(peerConn)
        print("Received sucessor one:",peerSuccessor1)
        # Add who we connected to to our finger table
        fingerTable[getHashIndex(peerSuccessor1)] = peerSuccessor1[0]+":"+str(peerSuccessor1[1])

        peerSuccessor2 = recvAddress(peerConn)
        print("Received sucessor one:",peerSuccessor1)
        # Add who we connected to to our finger table
        fingerTable[getHashIndex(peerSuccessor2)] = peerSuccessor2[0]+":"+str(peerSuccessor2[1])

        peerSuccessor1 = peerSuccessor1[0] +":"+ str(peerSuccessor1[1])
        peerSuccessor2 = peerSuccessor2[0] +":"+ str(peerSuccessor2[1])

        # Ensure we are not our own successor
        if peerSuccessor1[0] == myAddress[0] and peerSuccessor1[1] == myAddress[1]:
            peerSuccessor1 = peerIP +":"+ str(peerPort)

        numItems = recvInt(peerConn)
        if numItems == 0:
            print("Received zero files when connecting...")
            # Send peer we acknowledge we are supposed to receive nothing
            peerConn.send("T".encode())
        else:
            print("Receiving files...")
            for i in range(numItems):
                key = recvKey(peerConn)
                data = recvVal(peerConn)
                # Write the data to file
                with open("repo/"+str(key), 'wb') as f:
                    f.write(data)
            peerConn.send("T".encode())
        # End connection protocol #

        # Initializing my peer profile
        fingerTable[getHashIndex((getLocalIPAddress(), port))] = getLocalIPAddress() + ":" + str(port) # add ourselves
        myProfile = PeerProfile((getLocalIPAddress(),int(port)),fingerTable,peerSuccessor1,peerSuccessor2)

        #recv all protocol messages from peer we connected to
        print(menu)
        try:
            userInput = input("Command?\n")
        except KeyboardInterrupt:
            print("Rogue client...")
            doDisconnect()
        try:
            while True:
                if userInput == "1":
                    ##INSERT##
                    insertFile()

                elif userInput == "2":
                    ##REMOVE##
                    removeKey()

                elif userInput == "3":
                    ##GET##
                    getFile()

                elif userInput == "4":
                    ##EXISTS##
                    getExists()

                elif userInput == "5":
                    ##OWNS##
                    request_owns()

                elif userInput == "6":
                    ##DISCONNET##
                    doDisconnect()

                elif userInput == "7":
                    ##DIAGNOSTICS##
                    print(myProfile.serialize()) 

                elif userInput == "8":
                    ##UPDATE PROFILE##
                    myProfile.updateProfile(trueOwner) 

                else:
                    ##BOGUS##
                    print("What?")

                print(menu)
                userInput = input("Command?\n")

        except KeyboardInterrupt:
            print("Rogue client...")
            doDisconnect()

    else:
        pass
else:
    print("What you doing?")

