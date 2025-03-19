import os
import json
import socket

from lib.db import *

class User():
    
    def __init__(self, host): 

        self.ID = ""
        self.user = ""
        self.battery_level = ""
        self.vehicle = ""
        self.payment_method = ""
        self.payment_history = {}
        
        self.socket_sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        hostname = socket.gethostbyname(host)
        self.socket_sender.connect((hostname,8001))

    def sendRequest(self): #envia requisicao simples (para fins de teste)
        self.socket_sender.sendall(bytes('ok', 'UTF-8'))

    def batteryCheck(self): #notifica se a bateria esta em estado critico
        if self.battery_level < 0.3:
            return 1
        return 0
    
    def getID(self, requestID):

        msgList = ['', requestID, 'rve', '']
        
        msgString = json.dumps(msgList)
        self.socket_sender.sendall(bytes(msgString, 'UTF-8'))
        
        print(msgList)
        print(msgString)
        print(bytes(msgString, 'UTF-8'))

        msg = self.socket_sender.recv(1024)

        while (len(msg.decode('UTF-8')) != 24):
            self.socket_sender.sendall(bytes(msgString, 'UTF-8'))
            msg = self.socket_sender.recv(1024)

        if (int(requestID) < 63):
            requestID = str(int(requestID) + 1)
        else:
            requestID = "0"

        return msg.decode('UTF-8')
    
    def bookChargeSpot(self): #reserva posto
        self.socket_sender.sendall(bytes('reservar posto', 'UTF-8'))
        msg = self.socket_sender.recv(1024) #espera-se que o servidor responda se a reserva foi feita
        
        if msg.decode('UTF-8') =="s":
            print('reserva feita')
            return 1
        print('nao foi possivel fazer a reserva')

        if (int(requestID) < 63):
            requestID = str(int(requestID) + 1)
        else:
            requestID = "0"

        return 0
    
    def nearestSpotRequest(self): #solicita distancia do posto mais proximo
        self.socket_sender.sendall(bytes('distancia do posto', 'UTF-8'))
        msg = self.socket_sender.recv(1024)
        print('O posto mais proximo esta a',msg.decode('UTF-8')+'Km')
        
    def pay(self): #metodo que envia a solicitacao de pagamento ao servidor, recebe a confirmação e atualiza payment_history 
        return
    
    def paymentCheck(self): #visualiza payment_history
        print(self.payment_history)

#Programa inicia aqui
#Cria um objeto da classe User
vehicle = User("charge_server")

#Valores iniciais do programa
requestID = "0"

#Gera uma lista dos elementos presente no diretorio atual
fileList = os.listdir()

#Verifica se o arquivo de texto "ID.txt" esta presente, e caso nao esteja...
if (verifyFile([""], "ID.txt") == False):

    #Cria um novo arquivo
    createFile(["ID.txt"], vehicle.getID(requestID))

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
    createFile("vehicle_data.json", dataTable)

#Carrega as informacoes gravadas (ID)
vehicle_ID = readFile(["ID.txt"])

#Carrega as informacoes gravadas (vehicle_data)
loadedTable = readFile(["vehicle_data.json"])

#Modifica as informacoes do objeto do veiculo
vehicle.battery_level = loadedTable["battery_level"]

#Print de teste
print(vehicle.ID)
print(vehicle.battery_level)