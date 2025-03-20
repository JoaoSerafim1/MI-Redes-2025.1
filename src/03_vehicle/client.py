import os
import time
import json
import socket

from lib.db import *

class User():
    
    def __init__(self):

        self.ID = ""
        self.user = ""
        self.battery_level = ""
        self.vehicle = ""
        self.payment_method = ""
        self.payment_history = {}
        
    def sendRequest(self, serverName, request):

        socket_sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_sender.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket_sender.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        serializedRequest = json.dumps(request)
        SERVER = socket.gethostbyname(serverName)

        print("--------------------------------------------")
        print(serverName)
        print(SERVER)
        print(serializedRequest)
        print("--------------------------------------------")
        
        try:
            socket_sender.connect((SERVER, 8001))
            socket_sender.send(bytes(serializedRequest, 'UTF-8'))
            socket_sender.close()
        except Exception as err:
            print(err)

    def listenToResponse(self):

        socket_receiver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_receiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket_receiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        socket_receiver.settimeout(2.0)
        socket_receiver.bind((socket.gethostbyname(socket.gethostname()), 8002))
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
    
    def registerVehicle(self, requestID):

        requestContent = ['', requestID, 'rve', '']
        self.sendRequest('charge_server', requestContent)
        (add, response) = self.listenToResponse()

        while (len(response) != 24):
            self.sendRequest('charge_server', requestContent)
            (add, response) = self.listenToResponse()

        if (int(requestID) < 63):
            requestID = str(int(requestID) + 1)
        else:
            requestID = "0"

        return response

    def batteryCheck(self): #notifica se a bateria esta em estado critico
        if self.battery_level < 0.3:
            return 1
        return 0
    
    def bookChargeSpot(self, requestID): #reserva posto

        requestContent = ['', requestID, 'bcs', '']
        self.sendRequest('charge_server', requestContent)
        (add, response) = self.listenToResponse()

        while (len(response) != 1):
            self.sendRequest('charge_server', requestContent)
            (add, response) = self.listenToResponse()

        if (int(requestID) < 63):
            requestID = str(int(requestID) + 1)
        else:
            requestID = "0"

        return response
    
    def nearestSpotRequest(self, requestID): #solicita distancia do posto mais proximo
        
        requestContent = ['', requestID, 'nsr', '']
        self.sendRequest('charge_server', requestContent)
        (add, response) = self.listenToResponse()

        while (len(response) < 1):
            self.sendRequest('charge_server', requestContent)
            (add, response) = self.listenToResponse()

        if (int(requestID) < 63):
            requestID = str(int(requestID) + 1)
        else:
            requestID = "0"

        return response
        
    def pay(self): #metodo que envia a solicitacao de pagamento ao servidor, recebe a confirmação e atualiza payment_history 
        return
    
    def paymentCheck(self): #visualiza payment_history
        print(self.payment_history)

#Programa inicia aqui
#Cria um objeto da classe User
vehicle = User()

#Valores iniciais do programa
requestID = "0"

#Gera uma lista dos elementos presente no diretorio atual
fileList = os.listdir()

#Verifica se o arquivo de texto "ID.txt" esta presente, e caso nao esteja...
if (verifyFile([""], "ID.txt") == False):
    
    #Cria um novo arquivo
    createFile(["ID.txt"], vehicle.registerVehicle(requestID))

#Verifica se o arquivo de texto "vehicle_data.json" esta presente, e caso nao esteja...
if (verifyFile([""], "vehicle_data.json") == False):
    
    #...cria um dicionario dos atributos do veiculo e preenche com valores iniciais
    #Valores dos pares chave-valor sao sempre string para evitar problemas com json
    dataTable = {}
    dataTable["user"] = ""
    dataTable["battery_level"] = "1.0"
    dataTable["vehicle"] = ""
    dataTable["payment_method"] = ""
    dataTable["payment_history"] = ""

    #E tambem cria o arquivo e preenche com as informacoes contidas no dicionario acima
    createFile(["vehicle_data.json"], dataTable)

#Carrega as informacoes gravadas (ID)
vehicle.ID = readFile(["ID.txt"])

#Carrega as informacoes gravadas (vehicle_data)
loadedTable = readFile(["vehicle_data.json"])

#Modifica as informacoes do objeto do veiculo
vehicle.battery_level = loadedTable["battery_level"]

#Print de teste
print("*********************************************")
print(vehicle.ID)
print(vehicle.battery_level)
print("*********************************************")