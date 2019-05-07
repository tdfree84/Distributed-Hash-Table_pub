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
from peerProfile import *

menu = "--MENU--\nChoose 1 for: insert.\nChoose 2 for: remove.\nChoose 3 for: get.\nChoose 4 for: exists.\nChoose 5 for: owns.\nChoose 6 for: disconnect.\nChoose 7 for: finger table."


####################
# Helper functions #
####################

def trueOwner(number):

    candidate = owns(number)
    temp = candidate
    returned_peer = ''
    while candidate != returned_peer: 
        candidate = temp
        print("Calling:",candidate)
        conn = socket(AF_INET, SOCK_STREAM)
        connIP = candidate.split(':')[0]
        connPort = int(candidate.split(':')[1])

        conn.connect((connIP, connPort))
        conn.send("OWN".encode())
        sendKey(conn, number)

        returned_peer = recvAddress(conn)
        returned_peer = returned_peer[0] + ":" + str(returned_peer[1])
        temp = returned_peer
        print("They answered:",returned_peer)
        conn.close()

    return temp # If here, temp is the true owner


def owns(number):
    ''' Find the closest person to the hash number requested. '''
    myHash = getHashIndex(myProfile.myAddress)
    
    print("IT IS A:",myProfile.successor)
    s = myProfile.successor
    print("S: " + str(s))
    s = s.split(":")
    succHash = getHashIndex((s[0], int(s[1])))

    print("IAM: ")
    print("SUCC is:")
    print("Looking for:")
    print(myHash)
    print(succHash)
    print(number)
    print()

    hashes = list(myProfile.fingerTable.keys())
    hashes.sort(reverse=True)
    if number < myHash and number >= succHash:
        print('deleting my own hash')
        hashes.remove(myHash)   

    for i in range(len(hashes)):
        if number >= hashes[i]:
            #Establish connection to person we find
            #print(myProfile.fingerTable[hashes[i]])
            #print(myProfile.myAddrString())
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
                del myProfile.fingerTable[hashes[i]]
                return owns(number)

            t = recvAll(conn, 1)
            t = t.decode()
            if t == "T":
                conn.close()
                print("returned hash:")
                print(hashes[i])
                print()
                return myProfile.fingerTable[hashes[i]]

            conn.close()

    print(str(myProfile.fingerTable[hashes[0]]))
    print('returning largest value in fingertable')
    print("returned hash:")
    print(hashes[0])
    print()
    return myProfile.fingerTable[hashes[0]]

def request_owns():
    ''' Request an owns query from a peer. '''

    k = input("Enter a key: ")
    hashed_key = int.from_bytes(hashlib.sha1(k.encode()).digest(), byteorder="big")
    print(trueOwner(hashed_key))
   #requestConn = trueOwns(hashed_key)
   #requestConn = requestConn.split(":")
   #requestConnIP = requestConn[0]
   #requestConnPort = requestConn[1]
   #peerConn.send("OWN".encode()) # Say we want an owns query
   #sendKey(peerConn, hashed_key) # Send them hashed key

   #who = recvAddress(peerConn)
    #print("This is who might own it:",who)

def insertFile():
    ''' Inserts file into the DHT. '''


    keyName = input("What is the name of what you want to store? ")
    value = input("What exactly do you want to store? ")
    hashed_key = int.from_bytes(hashlib.sha1(keyName.encode()).digest(), byteorder="big")

    whoisit = trueOwner(hashed_key)
    print("This person owns it:",whoisit)
    ins = whoisit.split(":")
    insIP = ins[0]
    insPort = ins[1]
    insConn = socket(AF_INET, SOCK_STREAM)
    insConn.connect( (insIP, int(insPort)) )

    insConn.send("INS".encode()) # Tell them we want to insert

    # Send peer key of our data
    sendKey(insConn, int(hashed_key)) # Send them our data's hashed key

    tf = recvAll(insConn, 1) # Wait for them to respond
    tf = tf.decode()
    print("Receiving back from peer:",str(tf))
    if tf == "T":
        pass
    else:
        print("Something went wrong with your destination storage.")
        insConn.close()
        return

    # Send data if we can
    sendVal(insConn, value.encode())  # Send them the data

    tf = recvAll(insConn, 1) # Wait for them to respond
    tf = tf.decode()
    print("Receiving back from peer:",str(tf))
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

    whoisit = trueOwner(hashed_key)
    print("This person owns it:",whoisit)
    get = whoisit.split(":")
    getIP = get[0]
    getPort = get[1]
    getConn = socket(AF_INET, SOCK_STREAM)
    getConn.connect( (getIP, int(getPort)) )

    getConn.send("GET".encode())
    sendKey(getConn, hashed_key)


    # Receive peer response #
    tf = recvAll(getConn, 1)
    tf = tf.decode()
    print("Receiving from peer",tf)
    if tf == "T":
        print("Got a T..waiting on file.")
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

    whoisit = trueOwner(hashed_key)
    print("This person owns it:",whoisit)
    exi = whoisit.split(":")
    exiIP = exi[0]
    exiPort = exi[1]
    exiConn = socket(AF_INET, SOCK_STREAM)
    exiConn.connect( (exiIP, int(exiPort)) )

    exiConn.send("EXI".encode())
    sendKey(peerConn, hashed_key)

    # Receive peer response #
    tf = recvAll(exiConn, 1)
    tf = tf.decode()
    print("Receiving from peer",tf)
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
    
    whoisit = trueOwner(hashed_key)
    print("This person owns it:",whoisit)
    rem = whoisit.split(":")
    remIP = rem[0]
    remPort = rem[1]
    remConn = socket(AF_INET, SOCK_STREAM)
    remConn.connect( (remIP, int(remPort)) )
    
    remConn.send("REM".encode())
    sendKey(remConn, hashed_key)

    # Receive peer response #
    tf = recvAll(remConn, 1)
    tf = tf.decode()
    print("Receiving from peer",tf)
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
    ''' Disconncet from the DHT.  '''

    k = getHashIndex(myProfile.myAddress)-1

    whoisit = trueOwner(k)
    print("This person owns it:",whoisit)
    dis = whoisit.split(":")
    disIP = dis[0]
    disPort = dis[1]
    disConn = socket(AF_INET, SOCK_STREAM)
    disConn.connect( (disIP, int(disPort)) )
    k = getHashIndex(myProfile.myAddress)-1

    whoisit = trueOwner(k)
    print("This person owns it:",whoisit)
    dis = whoisit.split(":")
    disIP = rem[0]
    disPort = rem[1]
    disConn = socket(AF_INET, SOCK_STREAM)
    disConn.connect( (remIP, int(remPort)) )

    disConn.send("DIS".encode())
    sendAddress(disConn, myProfile.myAddress)

    # Receive peer response #
    tf = recvAll(disConn, 1)
    tf = tf.decode()
    print("Receiving from peer",tf)
    if tf == "T":
        print("Got a T, they are ready for us to disconnect")
    elif tf == "N":
        print("Peer doesn't own this space")
        return
        #rerun owns on the key
    else:
        print("IDK what happened.")
        return
        
    s = myProfile.successor.split(':')
    sendAddress(disConn, (s[0], int(s[1])))

    successorIP = myProfile.successor.split(':')[0]
    successorPort = int(myProfile.successor.split(':')[1])


    #send the number of items from their hash
    #get file names from repo
    fNameList = os.listdir('repo')
    listToSend = []
    for n in fNameList:
        nInt = int(n)
        if nInt < getHashIndex((successorIP, int(successorPort))) and nInt > getHashIndex((disIP, int(disPort))):
            listToSend.append(n)

    sendInt(disConn, len(listToSend))

    #for number of items, send [key][valSize][val] to peer
    for n in listToSend:
        f = open('repo/' + n, 'rb')
        fBytes = f.read()
        sendKey(disConn, int(n))
        sendVal(disConn, fBytes) 
        f.close()

    # Receive peer response #
    tf = recvAll(disConn, 1)
    tf = tf.decode()
    print("Receiving from peer",tf)
    if tf == "T":
        print("Got a T, they accepted everything")
    else:
        print("IDK what happened.")
        return
    
    # Fully disconnect
    print("bye")
    sys.exit(0)



######################
# Helper function(s) #
######################

def makeFingerTable(randKeyRange, peerIP, peerPort, flag):
    #fingerTable = {}
    #fingerTable[getHashIndex(myProfile.myAddress)] = myProfile.myAddrString()
    #if flag == True:
    fingerTable[getHashIndex((peerIP, int(peerPort)))] = peerIP + ":" + str(peerPort)

    offset = randKeyRange

    for i in range(5):
        who = trueOwner(offset)
        print("Owns: ",who)
        who_spl = who.split(':')
        who_tup = (who_spl[0],int(who_spl[1]))
        fingerTable[offset] = who
        offset += randKeyRange

    myProfile.fingerTable = fingerTable




#################
# Peer handling #
#################

def handlePeer(peerInfo):
    ''' handlePeer receives commands from a client sending requests. '''

    #handle a new client that connects
    print("I have connected with someone.")
    peerConn, peerAddr = peerInfo
    while True:
        conMsg = recvAll(peerConn, 3)
        conMsg = conMsg.decode()
        if conMsg!='' and conMsg!='\n' and conMsg != ' ':
            print(conMsg)
        if conMsg == "CON":
            peerIP, peerPort = recvAddress(peerConn)
            print("THIS PERSON IS CONNECTING: " + peerIP + ":" + str(peerPort))
            print(peerIP + ":" + str(peerPort))
            print(myProfile.myAddrString())
            peerHash = getHashIndex((peerIP, peerPort))
            myHash = getHashIndex((myProfile.myAddress[0], myProfile.myAddress[1]))
            
            successor = myProfile.successor.split(":")
            successorIP = successor[0]
            successorPort = successor[1]
            successorHash = getHashIndex((successorIP, int(successorPort)))

           #if peerHash < myHash:
           #    if peerHash >= 0 and peerHash < successorHash or peerHash > myHash and peerHash< 2**160:
           #        print('connect is less than us')
           #        peerConn.send("T".encode())

           #elif myProfile.successor == myProfile.myAddrString():
           #    print('successor conditional')
           #    peerConn.send("T".encode())

           #elif peerHash > myHash and peerHash < successorHash:
           #    print('between us')
            if trueOwner(peerHash) == myProfile.myAddrString():
                peerConn.send("T".encode())
            else:
                peerConn.send("N".encode())
                continue
            #if owns(getHashIndex((peerIP, peerPort))) == myProfile.myAddrString():
                #####################
                #CONNECTION PROTOCOL#
                #####################

            #sending them a T if we own they space they want
            print("T\n")
            #peerConn.send('T'.encode())
            #update our fingertable
            #WE NEED TO PASS UP OUR PEER INFO
            fingerTable[getHashIndex((peerIP, int(peerPort)))] = peerIP + ":" + str(peerPort)
            #tf = True
            #makeFingerTable(randKeyRange, peerIP, peerPort, tf)
            print("My finger table is", myProfile.fingerTable)

            #send the address of our successor
            successor = myProfile.successor.split(":")
            successorIP = successor[0]
            successorPort = successor[1]

            sendAddress(peerConn, (successorIP, int(successorPort)))

            #send the number of items from their hash
            #get file names from repo
            fNameList = os.listdir('repo')
            listToSend = []
            for n in fNameList:
                nInt = int(n)
                if nInt < getHashIndex((successorIP, int(successorPort))) and nInt > getHashIndex((peerIP, int(peerPort))):
                    listToSend.append(n)

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
                #once done, we no longer own that keyspace, so update
                #our keyspace ranges
                print("updating SUECCESOOR")
                myProfile.successor = peerIP + ":" + str(peerPort)
           #else:
           #    #send this if we don't own the space they want
           #    print("N")
           #    peerConn.send("N".encode())
        elif conMsg == "DIS":
            
            peerAddr = recvAddress(peerConn)
            peerAddrStr = peerAddr[0] + ":" + str(peerAddr[1])
            #print(myProfile.myAddrString())
            if trueOwner(getHashIndex((peerAddr[0], peerAddr[1]))-1) == myProfile.myAddrString():
                #####################
                #DISCONNECT PROTOCOL#
                #####################

                #sending them a T if we own they space they want
                print("T\n")
                peerConn.send('T'.encode())

                #receive address of our new successor
                successor = recvAddress(peerConn)
                successorIP = successor[0]
                successorPort = successor[1]

                numItems = recvInt(peerConn)

                for n in range(numItems):
                    try:
                        k = recvKey(peerConn)
                        print("File key: " + k)
                        data = recvVal(peerConn)
                        print("File data: " + data)
                        f = open('repo/' + k, 'wb')
                        print("open file data")
                        f.write(data)
                        f.close()
                    except:
                        print("Failed to write some data when peer was disconnecting")
                
                peerConn.send("T".encode())
                peerConn.close()

                #update our info
                myProfile.successor = successorIP + ":" + str(successorPort)
                #put fingertable function in right here to update table
                fingerTable[getHashIndex((successorIP, int(successorPort)))] = successorIP + ":" + str(successorPort)
                #tf = True
                #makeFingerTable(randKeyRange, successorIP, successorPort, tf)
                print("My finger table is",myProfile.fingerTable)

                break

            else:
                #send this if we don't own the space they want
                print("N")
                peerConn.send("N".encode())



        elif conMsg == "INS":
            #################
            #INSERT PROTOCOL#
            #################
            fileName = recvKey(peerConn)
            o = owns(fileName)

            #if we own the space, send positive confirmation
            successor = myProfile.successor.split(":")
            successorIP = successor[0]
            successorPort = successor[1]

            print("My Successor Key: " +str(getHashIndex((successorIP, int(successorPort)))))
            print("File Key:         " + str(fileName))
            print("My Key:           " + str(getHashIndex(myProfile.myAddress)))
            print("My successor: " + myProfile.successor)
            successorHash = getHashIndex((successorIP, int(successorPort)))
            myHash = getHashIndex(myProfile.myAddress)


            #MADE CHANGES TO INSERT, FIXED SUCCESSOR PROBLEM
           #if successorHash < myHash:
           #    if fileName >= 0 and fileName < successorHash or fileName >= myHash and fileName< 2**160:
           #        peerConn.send("T".encode())

           #elif fileName >= myHash and fileName < successorHash:
            if trueOwner(fileName) == myProfile.myAddrString():
                peerConn.send("T".encode())
            else:
                peerConn.send("N".encode())
                continue

            print("PEERNAME :" + o)
            print("FILENAME: " + str(fileName))
            print("MY NAME: " + myProfile.myAddrString())

            try:
                print("I own this.")
                fileContent = recvVal(peerConn)
                print("FILE: " + str(fileContent))
                f = open('repo/' + str(fileName), 'wb')
                f.write(fileContent)
                f.close()
                peerConn.send("T".encode())
            except:
                peerConn.send("F".encode())

        elif conMsg == "OWN":
            key = recvKey(peerConn)
            owner = owns(key)
            #do a pulse check here

            ownerList = owner.split(":")
            ownerIP = ownerList[0]
            ownerPort = int(ownerList[1])
            sendAddress(peerConn, (ownerIP, ownerPort))

        elif conMsg == "GET":
            key = recvKey(peerConn)
            print("Key to Get: " + str(key))

            if trueOwner(key) == myProfile.myAddrString():
                print("in get")
                try:
                    f = open("repo/"+str(key), "rb")
                    print("reading file")
                    fileToSend = f.read()
                    peerConn.send("T".encode())
                    sendVal(peerConn, fileToSend)
                    f.close()
                except:
                    peerConn.send("F".encode())
            else:
                peerConn.send("N".encode())

        elif conMsg == "EXI":
            key = recvKey(peerConn)

            if trueOwner(key) == myProfile.myAddrString():
                try:
                    f=open("repo/"+str(key), "rb")
                    peerConn.send("T".encode())
                except:
                    peerConn.send("F".encode())
            else:
                peerConn.send("N".encode())

        elif conMsg == "REM":
            key = recvKey(peerConn)
            keyStr = str(key)

            if trueOwner(key) == myProfile.myAddrString():
                try:
                    f=open("repo/"+keyStr, "rb")
                    os.remove("repo/"+keyStr)
                    if not (os.path.exists("repo/"+keyStr)):
                        peerConn.send("T".encode())
                except:
                    peerConn.send("F".encode())
            else:
                peerConn.send("N".encode())

        elif conMsg == "PUL":
            peerConn.send("T".encode())
            peerConn.close()
            break

        elif conMsg == "INF":
            fingerString = myProfile.serialize()
            sendVal(peerConn, fingerString)

    return


def waitForPeerConnections(listener):
    ''' waitForPeerConnections listens for other peers to connect to us and spawns off a new thread for each peer that connects. '''

    while running:
        peerInfo = listener.accept()
        threading.Thread(target=handlePeer, args = (peerInfo,), daemon=True).start()



####################################
#######                      #######
######  BEGINNING OF RUNNING  ######
#######                      #######
####################################

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
# THIS client's profile
myProfile = ''

# Seed client is len == 1
if len(sys.argv) == 1:
    #set up our own thread to start listening for clients
    print("This is a the seed client")
    threading.Thread(target=waitForPeerConnections, args = (listener,), daemon=True).start()
    addr = getLocalIPAddress() + ":" + str(port)
    fingerTable[getHashIndex((getLocalIPAddress(), int(port)))] = addr
    #fingerTable[0] = addr

    print(menu)
    ourHash = getHashIndex((getLocalIPAddress(), int(port)))

    # Initializing my peer profile
    myProfile = PeerProfile((getLocalIPAddress(),int(port)),fingerTable,addr,addr)

    #tf = False
    #makeFingerTable(randKeyRange, 0 , 0, tf)
    #fingerTable[getHashIndex((successorIP, int(successorPort))] = successorIP + ":" + int(successorPort)

    print("My finger table is",myProfile.fingerTable)

    userInput = input("Command?")
    while userInput != "disconnect":
        print("Running")
        print(menu)

    #DOESNT WORK
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
        
        else:
            ##BOGUS##
            print("What?")

        userInput = input("Command?\n")
    
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

    myAddress = (getLocalIPAddress(), port)
    fingerTable[getHashIndex((peerIP, peerPort))] = peerIP + ":" + str(peerPort)
    myAddressString = myAddress[0] + ":" + str(myAddress[1])
    myProfile = PeerProfile((getLocalIPAddress(),int(port)),fingerTable,myAddressString,myAddressString)

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
        print("Received T, good to connect.")
       
        # Gathering info for our profile
        addr = getLocalIPAddress() + ":" + str(port)
        # Add ourselves to the finger table
        fingerTable[getHashIndex((getLocalIPAddress(), int(port)))] = addr 
        # Add who we just connected to
        #fingerTable[getHashIndex((peerIP, int(peerPort)))] = peerIP +":"+ str(peerPort)
        
        # Set our keyspace (THIS IS WRONG AND NEES TO CHANGE)
        ourHash = getHashIndex((getLocalIPAddress(), int(port)))
        
        # Finish out rest of connection protocol after we have the ok to continue #
        peerSuccessor = recvAddress(peerConn)
        print("My received connection protocol cucessor is:",peerSuccessor)
        fingerTable[getHashIndex(peerSuccessor)] = peerSuccessor[0]+":"+str(peerSuccessor[1])
        peerSuccessor = peerSuccessor[0] +":"+ str(peerSuccessor[1])

        numItems = recvInt(peerConn)
        if numItems == 0:
            print("Received zero")
            # Send peer we acknowledge we are supposed to receive nothing
            peerConn.send("T".encode())
        else:
            for i in range(numItems):
                print("Receiving file..")
                key = recvKey(peerConn)
                data = recvVal(peerConn)
                # Write the data to file
                with open("repo/"+str(key), 'wb') as f:
                    f.write(data)
            peerConn.send("T".encode())
        # End connection protocol #

        # Initializing my peer profile
        myProfile = PeerProfile((getLocalIPAddress(),int(port)),fingerTable,peerSuccessor,peerSuccessor)
        print("MY PEER SUCCESSOR: " + myProfile.successor)

        #tf = True
        #makeFingerTable(randKeyRange, peerSuccessor[0], peerSuccessor[1], tf)

        print("My finger table is",myProfile.fingerTable)

        #recv all protocol messages from peer we connected to
        print(menu)
        userInput = input("Command?\n")

        while userInput != "disconnect":
            print(menu)

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
                print(myProfile.fingerTable) 

            else:
                ##BOGUS##
                print("What?")
                
            userInput = input("Command?\n")
    else:
        pass
        #run owns on our hash
else:
    print("What you doing?")

