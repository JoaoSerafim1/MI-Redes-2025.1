import os
import json
import socket

from lib.db import *

class User():
    
    def __init__(self, user, battery_level, vehicle, payment_method, host): 

        self.user = user
        self.battery_level = battery_level
        self.vehicle = vehicle
        self.payment_method = payment_method
        self.payment_history = {}
        
        self.socket_sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        hostname = socket.gethostbyname(host)
        self.socket_sender.connect((hostname,8001))

    def sendRequest(self): #envia requisicao simples (para fins de teste)
        self.socket_sender.sendall((str.encode('ok')))

    def batteryCheck(self): #notifica se a bateria esta em estado critico
        if self.battery_level < 0.3:
            return 1
        return 0
    
    def getID(self):

        msgList = ['', requestID, 'rve', '']
        msgString = json.dumps(msgList)

        self.socket_sender.sendall((str.encode(msgString)))
        
        msg = self.socket_sender.recv(1024)

        while (len(msg.decode()) != 24):
            self.socket_sender.sendall((str.encode(msgString)))
            msg = self.socket_sender.recv(1024)

        if (int(requestID) < 63):
            requestID = str(int(requestID) + 1)
        else:
            requestID = "0"

        return msg.decode()
    
    def bookChargeSpot(self): #reserva posto
        self.socket_sender.sendall((str.encode('reservar posto')))
        msg = self.socket_sender.recv(1024) #espera-se que o servidor responda se a reserva foi feita
        
        if msg.decode() =="s":
            print('reserva feita')
            return 1
        print('nao foi possivel fazer a reserva')

        if (int(requestID) < 63):
            requestID = str(int(requestID) + 1)
        else:
            requestID = "0"

        return 0
    
    def nearestSpotRequest(self): #solicita distancia do posto mais proximo
        self.socket_sender.sendall((str.encode('distancia do posto')))
        msg = self.socket_sender.recv(1024)
        print('O posto mais proximo esta a',msg.decode()+'Km')
        
    def pay(self): #metodo que envia a solicitacao de pagamento ao servidor, recebe a confirmação e atualiza payment_history 
        return
    
    def paymentCheck(self): #visualiza payment_history
        print(self.payment_history)

#Programa inicia aqui
#Cria um objeto da classe User
vehicle = User("", "", "", "","charge_server")

#Valores iniciais do programa
requestID = "0"

#Gera uma lista dos elementos presente no diretorio atual
fileList = os.listdir()

#Verifica se o arquivo de texto "ID.txt" esta presente, e caso nao esteja...
if (verifyFile([""], "ID.txt") == False):

    #Cria um novo arquivo
    createFile(["ID.txt"], vehicle.getID())

#Verifica se o arquivo de texto "vehicle_data.json" esta presente, e caso nao esteja...
if (verifyFile([""], "vehicle_data.txt") == False):
    
    #...cria um dicionario dos atributos do veiculo e preenche com valores iniciais
    #Valores dos pares chave-valor sao sempre string para evitar problemas com json
    dataTable = {}
    dataTable["user"] = ""
    dataTable[""]
    dataTable["battery_level"] = "1.0"

    #E tambem cria o arquivo e preenche com as informacoes contidas no dicionario acima
    dataFile = open("vehicle_data.json", "w")
    json.dump(dataTable, dataFile)
    dataFile.close()

#Carrega as informacoes gravadas (ID)
vehicle_ID = readFile(["ID.txt"])

#Carrega as informacoes gravadas (vehicle_data)
loadedTable = readFile(["vehicle_data.json"])

#Modifica as informacoes do objeto do veiculo
vehicle.battery_level = loadedTable["battery_level"]

#Print de teste
print(vehicle.ID)
print(vehicle.battery_level)