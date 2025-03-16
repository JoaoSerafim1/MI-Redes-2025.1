import socket
import json
import os

requestBook = {}

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

def freeChargeSpot(clientID):
    
    stationFilePath = (os.path.join("clientdata", "stations", (clientID + ".json")))

    try:

        stationFile = open(stationFilePath, "x")

    except:
        
        stationFile = open(stationFilePath, "r")
        stationInfo = json.load(stationFile)
        stationFile.close()

        stationInfo["available_spots"] = str(int(stationInfo["available_spots"]) + 1)

        stationFile = open(stationFilePath, "w")
        json.dump(stationInfo, stationFile)
        stationFile.close()

while (1==1):
    
    clientAddress, requestInfo = listenToRequest

    clientID = requestInfo[0]
    requestID = requestInfo[1]
    requestName = requestInfo[2]
    requestParameters = requestInfo[3]

    if (((clientID in requestBook) == False) or (requestBook[clientID] != requestID)):
        
        requestBook[clientID] = requestID
        
        if (requestName == "fcs"):
            freeChargeSpot(clientID)
    
    socket_sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    CLIENT = socket.gethostbyaddr(clientAddress)
    socket_sender.connect((CLIENT, 8002))
    socket_sender.send(bytes('ok', 'UTF-8'))