import os
import string
import random
import socket
import json

from lib.db import *

class Server():
    
    def __init__(self):

        self.requestLog = {}

    def getRandomID(self, actualRandom):

        lettersanddigits = string.ascii_uppercase + string.digits

        while True:

            randomID = ""

            for count in range(0,24):
                randomID += random.choice(lettersanddigits)

            completeFileName = (randomID + ".json")
            
            if ((verifyFile(["clientdata", "clients"], completeFileName)) == False and (randomID != actualRandom)):
                
                return randomID

    def listenToRequest(self):

        socket_receiver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_receiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket_receiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        socket_receiver.settimeout(2.0)
        socket_receiver.bind((socket.gethostbyname(socket.gethostname()), 8001))
        socket_receiver.listen(2)

        msg = bytes([])
        add = ""
        
        try:
            conn, add = socket_receiver.accept()
            msg = conn.recv(1024)
            socket_receiver.close()
        except:
            pass
        
        decodedBytes = msg.decode('UTF-8')
        
        if (len(decodedBytes) > 0):

            print("=============================================")
            print(add)
            print(msg)
            print(decodedBytes)
            print("=============================================")
            
            unserializedObj = json.loads(decodedBytes)

            return (add, unserializedObj)
        
        return (add, "")
    
    def sendResponse(self, clientAddress, response):

        socket_sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_sender.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket_sender.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        clientAddressString, clientPID = clientAddress
        serializedResponse = json.dumps(response)

        print("--------------------------------------------")
        print(clientAddress)
        print(clientAddressString)
        print(serializedResponse)
        print("--------------------------------------------")
        
        try:
            socket_sender.connect((clientAddressString, 8002))
            socket_sender.send(bytes(serializedResponse, 'UTF-8'))
            socket_sender.close()
        except Exception as err:
            print(err)

    def registerChargeStation(self, requestID, stationAddress, randomID, requestParameters):
        
        stationID = requestParameters[0]
        stationAddressString = json.dumps(stationAddress)

        if ((len(stationInfo) >= 4) and stationID == randomID):
            
            stationInfo = {}
            stationInfo["coordinates"] = requestParameters[1]
            stationInfo["available_spots"] = requestParameters[2]
            stationInfo["unitary_price"] = requestParameters[3]
            
            fileName = (randomID + ".json")
            createFile(["clientdata", "clients", fileName], stationInfo)

            self.requestLog[stationAddressString] = [requestID, 'OK']
            self.sendResponse(stationAddress, 'OK')

            newRandomID = self.getRandomID(randomID)
            print("ID para o proximo cadastro de estacao de carga: " + newRandomID)
            return newRandomID
        
        else:

            self.requestLog[stationAddressString] = [requestID, 'ERR']
            self.sendResponse(stationAddress, 'ERR')

    def registerVehicle(self, requestID, vehicleAddress, randomID):

        vehicleAddressString = json.dumps(vehicleAddress)
        self.requestLog[vehicleAddressString] = [requestID, randomID]
        self.sendResponse(vehicleAddress, self.getRandomID(randomID))
        

#Programa inicia aqui
localServer = Server()

randomID = localServer.getRandomID("*")
print("ID para o proximo cadastro de estacao de carga: " + randomID)

requestResult = ""

while True:
    
    clientAddress, requestInfo = localServer.listenToRequest()
    clientAddressString = json.dumps(clientAddress)

    if (len(requestInfo) >= 4):
        
        clientID = requestInfo[0]
        requestID = requestInfo[1]
        requestName = requestInfo[2]
        requestParameters = requestInfo[3]

        if (((clientAddressString in localServer.requestLog) == False) or (localServer.requestLog[clientAddressString][0] != requestID)):
            
            if (requestName == 'rcs'):
                localServer.registerChargeStation(requestID, clientAddress, randomID, requestParameters)
            if (requestName == 'rve'):
                localServer.registerVehicle(requestID, clientAddress, randomID)

        else:

            localServer.sendResponse(clientAddress, localServer.requestLog[clientAddressString][1])

    
    else:

        if clientAddress != "":
            
            localServer.sendResponse(clientAddress, 'ERR')