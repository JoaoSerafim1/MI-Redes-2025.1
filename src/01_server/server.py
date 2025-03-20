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

    def getRandomID(self):
        
        fileList = os.listdir("clientdata")

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
        
        print(add)
        print(msg)
        print(decodedBytes)
        
        if (len(decodedBytes) > 0):
            unserializedObj = json.loads(decodedBytes)

            return (add, unserializedObj)
        
        return (add, "")

    def registerChargeStation(self, requestParameters, stationAddress):
        
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

    def registerVehicle(self, server, vehicleAddress, requestID):
        
        vehicleID = server.getRandomID()

        server.requestLog[vehicleAddress] = [requestID, vehicleID]

        socket_sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        CLIENT = socket.gethostbyaddr(vehicleAddress)
        socket_sender.connect((CLIENT[0], 8002))
        socket_sender.send(bytes(vehicleID, 'UTF-8'))

#Programa inicia aqui
localServer = Server()

randomID = localServer.getRandomID()

requestResult = ""

while True:
    
    clientAddress, requestInfo = localServer.listenToRequest()
    clientAddressString = ("" + clientAddress[0] + ":" + str(clientAddress[1]))
    print("A")

    if (len(requestInfo) >= 4):
        
        clientID = requestInfo[0]
        requestID = requestInfo[1]
        requestName = requestInfo[2]
        requestParameters = requestInfo[3]

        if (((clientAddressString in localServer.requestLog) == False) or (localServer.requestLog[clientAddressString][0] != requestID)):
            
            localServer.requestLog[clientID] = requestID
            
            if (requestName == 'rcs'):
                requestResult = lastmsg = localServer.registerChargeStation(requestParameters, clientAddressString)
            if (requestName == 'rve'):
                requestResult = localServer.registerVehicle(localServer, clientAddress[0], requestID)

            localServer.requestLog[clientAddressString] = [requestID, requestResult]

        else:

            socket_sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            CLIENT = socket.gethostbyaddr(clientAddressString)
            socket_sender.connect((CLIENT, 8002))
            socket_sender.sendall((localServer.requestLog[clientAddressString][1]).encode())
    
    else:

        socket_sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        CLIENT = socket.gethostbyaddr(clientAddressString)
        socket_sender.connect((CLIENT, 8002))
        socket_sender.send(bytes('ERR', 'UTF-8'))