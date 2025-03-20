import os
import string
import random
import socket
import json

from lib.db import *

class Server():
    
    def __init__(self):

        self.requestLog = {}

        self.socket_receiver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_receiver.bind((socket.gethostbyname('charge_server'), 8001))

        self.socket_sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def getRandomID(self):

        lettersanddigits = string.ascii_uppercase + string.digits

        while True:

            randomID = ""

            for count in range(0,24):
                randomID += random.choice(lettersanddigits)

            completeFileName = (randomID + ".json")
            
            if verifyFile(["clientdata", "clients"], completeFileName) == False:
                
                print("ID para o proximo cadastro de estacao de carga: " + randomID)
                return randomID

    def listenToRequest(self):
        
        self.socket_receiver.listen(2)
        conn, add = self.socket_receiver.accept()
        msg = conn.recv(1024)
        
        decodedBytes = msg.decode('UTF-8')
        
        print(add)
        print(msg)
        print(decodedBytes)
        
        if (len(decodedBytes) > 0):
            unserializedObj = json.loads(decodedBytes)

            return (add, unserializedObj)
        
        return (add, "")
    
    def sendResponse(self, clientAddress, response):
        
        serializedResponse = json.dumps(response)
        CLIENT = socket.gethostbyaddr(clientAddress[0])
        
        try:
            self.socket_sender.connect((CLIENT[0], 8002))
            self.socket_sender.send(bytes(serializedResponse, 'UTF-8'))
        except Exception:
            pass

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

            randomID = self.getRandomID()
        
        else:

            self.requestLog[stationAddressString] = [requestID, 'ERR']
            self.sendResponse(stationAddress, 'ERR')

    def registerVehicle(self, requestID, vehicleAddress, randomID):

        vehicleAddressString = json.dumps(vehicleAddress)
        self.requestLog[vehicleAddressString] = [requestID, randomID]
        self.sendResponse(vehicleAddress, randomID)

        randomID = self.getRandomID()

        

#Programa inicia aqui
localServer = Server()

randomID = localServer.getRandomID()

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

        localServer.sendResponse(clientAddress, 'ERR')