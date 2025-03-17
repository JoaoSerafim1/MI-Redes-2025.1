import socket
import json
import os
import string
import random

requestBook = {}

def getRandomID(type):
    
    lettersanddigits = string.ascii_uppercase + string.digits

    while True:
        
        randomID = ""

        for count in range(0,24):
            randomID += random.choice(lettersanddigits)
        
        try:
            
            if (type == 0):

                stationFilePath = (os.path.join("clientdata", "stations", (randomID + ".json")))
                open(stationFilePath, "r")
            
            else:

                vehicleFilePath = (os.path.join("clientdata", "vehicles", (randomID + ".json")))
                open(vehicleFilePath, "r")
            
        except:
            
            print("ID para cadastro do proximo posto de recarga: " + randomID)
            return randomID

def listenToRequest():
    
    socket_receiver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    HOST = socket.gethostbyname('charge_server')
    socket_receiver.bind((HOST, 8001))
    socket_receiver.listen(2)
    conn, add = socket_receiver.accept()
    msg = conn.recv(1024)
    
    decodedBytes = msg.decode('UTF-8')
    unserializedObj = json.loads(decodedBytes)

    return (add, unserializedObj)

def registerChargeStation(requestParameters, stationAddress):
    
    stationID = requestParameters[0]

    socket_sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    CLIENT = socket.gethostbyaddr(stationAddress)
    socket_sender.connect((CLIENT, 8002))
    
    if (len(stationInfo) >= 4) and stationID == randomID:
        
        stationFilePath = (os.path.join("clientdata", "stations", (stationID + ".json")))
        
        stationInfo = {}
        stationInfo["coordinates"] = requestParameters[1]
        stationInfo["available_spots"] = requestParameters[2]
        stationInfo["unitary_price"] = requestParameters[3]
        
        stationFile = open(stationFilePath, "w")
        json.dump(stationInfo, stationFile)
        stationFile.close()

        socket_sender.send(bytes('OK', 'UTF-8'))
    
    else:
        socket_sender.send(bytes('ERR', 'UTF-8'))

def freeChargeSpot(stationID, stationAddress):
    
    stationFilePath = (os.path.join("clientdata", "stations", (stationID + ".json")))

    try:

        stationFile = open(stationFilePath, "x")

    except:
        
        stationFile = open(stationFilePath, "r")
        stationInfo = json.load(stationFile)
        stationFile.close()

        try:

            stationInfo["available_spots"] = str(int(stationInfo["available_spots"]) + 1)

            stationFile = open(stationFilePath, "w")
            json.dump(stationInfo, stationFile)
            stationFile.close()

            socket_sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            CLIENT = socket.gethostbyaddr(stationAddress)
            socket_sender.connect((CLIENT, 8002))
            socket_sender.send(bytes('OK', 'UTF-8'))
        
        except:

            print("ERR: BAD REGISTRY FILE at <" + stationFilePath + ">")

def occupyChargeSpot(stationID, stationAdress):
    
    stationFilePath = (os.path.join("clientdata", "stations", (stationID + ".json")))

    try:

        stationFile = open(stationFilePath, "x")

    except:
        
        stationFile = open(stationFilePath, "r")
        stationInfo = json.load(stationFile)
        stationFile.close()

        try:
            
            stationInfo["available_spots"] = str(int(stationInfo["available_spots"]) - 1)

            stationFile = open(stationFilePath, "w")
            json.dump(stationInfo, stationFile)
            stationFile.close()

            socket_sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            CLIENT = socket.gethostbyaddr(stationAdress)
            socket_sender.connect((CLIENT, 8002))
            socket_sender.send(bytes('OK', 'UTF-8'))
        
        except:

            print("ERR: BAD REGISTRY FILE at <" + stationFilePath + ">")

#Programa inicia aqui
randomID = getRandomID(0)

while True:
    
    clientAddress, requestInfo = listenToRequest

    if (len(requestInfo >= 4)):
        
        clientID = requestInfo[0]
        requestID = requestInfo[1]
        requestName = requestInfo[2]
        requestParameters = requestInfo[3]

        if (((clientID in requestBook) == False) or (requestBook[clientID] != requestID)):
            
            requestBook[clientID] = requestID
            
            if (requestName == "rcs"):
                registerChargeStation(requestParameters, clientAddress)
            elif (requestName == "fcs"):
                freeChargeSpot(clientID, clientAddress)
            elif (requestName == "ocs"):
                occupyChargeSpot(clientID, clientAddress)
    
    else:

        socket_sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        CLIENT = socket.gethostbyaddr(clientAddress)
        socket_sender.connect((CLIENT, 8002))
        socket_sender.send(bytes('ERR', 'UTF-8'))