import os
import string
import random
import socket
import json

class Server():
    
    def __init__(self):

        self.requestLog = {}
        self.socket_receiver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_receiver.bind((socket.gethostbyname('charge_server'), 8001))

    def getRandomID(type):

        filePath = ""
            
        if (type == 0):
            filePath = os.path.join("clientdata", "stations")
        else:
            filePath = os.path.join("clientdata", "vehicles")
        
        fileList = os.listdir(filePath)

        lettersanddigits = string.ascii_uppercase + string.digits

        while True:

            randomID = ""

            for count in range(0,24):
                randomID += random.choice(lettersanddigits)
            
            if (("" + randomID + ".json") not in fileList):
                
                print("ID para o proximo cadastro de estacao de carga: " + randomID)
                return randomID

    def listenToRequest(self):
        
        self.socket_receiver.listen(2)
        conn, add = self.socket_receiver.accept()
        msg = conn.recv(1024)
        
        decodedBytes = msg.decode('UTF-8')
        unserializedObj = json.loads(decodedBytes)

        return (add, unserializedObj)

    def registerChargeStation(requestParameters, stationAddress):
        
        stationID = requestParameters[0]

        socket_sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        CLIENT = socket.gethostbyaddr(stationAddress)
        socket_sender.connect((CLIENT, 8002))
        
        if ((len(stationInfo) >= 4) and stationID == randomID):
            
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

    def registerVehicle(vehicleAddress):
        
        vehicleID = self.get
        
        if ((len(stationInfo) >= 4) and vehicleID == randomID):
            
            stationFilePath = (os.path.join("clientdata", "stations", (vehicleID + ".json")))
            
            stationInfo = {}
            stationInfo["coordinates"] = requestParameters[1]
            stationInfo["available_spots"] = requestParameters[2]
            stationInfo["unitary_price"] = requestParameters[3]
            
            stationFile = open(stationFilePath, "w")
            json.dump(stationInfo, stationFile)
            stationFile.close()

            socket_sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            CLIENT = socket.gethostbyaddr(vehicleAddress)
            socket_sender.connect((CLIENT, 8002))
            socket_sender.send(bytes('OK', 'UTF-8'))
        
        else:
            socket_sender.send(bytes('ERR', 'UTF-8'))

#Programa inicia aqui
localServer = Server()

randomID = localServer.getRandomID(0)

while True:
    
    clientAddress, requestInfo = localServer.listenToRequest()

    if (len(requestInfo >= 4)):
        
        clientID = requestInfo[0]
        requestID = requestInfo[1]
        requestName = requestInfo[2]
        requestParameters = requestInfo[3]

        if (((clientID in localServer.requestBook) == False) or (localServer.requestBook[clientID] != requestID)):
            
            localServer.requestBook[clientID] = requestID
            
            if (requestName == 'rcs'):
                localServer.registerChargeStation(requestParameters, clientAddress)
            if (requestName == 'rve'):
                localServer.registerVehicle(clientAddress)
    
    else:

        socket_sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        CLIENT = socket.gethostbyaddr(clientAddress)
        socket_sender.connect((CLIENT, 8002))
        socket_sender.send(bytes('ERR', 'UTF-8'))