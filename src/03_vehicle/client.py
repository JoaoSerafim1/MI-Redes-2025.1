import os
import json
import socket

class User():
    
    def __init__(self, ID, user, battery_level, vehicle, payment_method, host): 
        
        self.ID = ID
        self.battery_level = battery_level
        self.user = user
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
    
    def getNewID(self):
        self.socket_sender.sendall((str.encode('getID')))
        msg = self.socket_sender.recv(1024)

        while (len(msg.decode()) != 24):
            self.socket_sender.sendall((str.encode('getID')))
            msg = self.socket_sender.recv(1024)

        return msg.decode()
    
    def bookChargeSpot(self): #reserva posto
        self.socket_sender.sendall((str.encode('reservar posto')))
        msg = self.socket_sender.recv(1024) #espera-se que o servidor responda se a reserva foi feita
        
        if msg.decode() =="s":
            print('reserva feita')
            return 1
        print('nao foi possivel fazer a reserva')
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
vehicle = User("", "", "", "", "", "charge_server")

#Gera uma lista dos elementos presente no diretorio atual
fileList = os.listdir()

#Verifica se o arquivo de texto "ID.txt" esta presente, e caso nao esteja...
if ("ID.txt" not in fileList):
    
    #...cria o arquivo e preenche com um novo ID
    idFile = open("ID.txt", "w")
    idFile.write(vehicle.getNewID())
    idFile.close()

#Verifica se o arquivo de texto "vehicle_data.json" esta presente, e caso nao esteja...
if ("vehicle_data.json" not in fileList):
    
    #...cria um dicionario dos atributos dos veiculos e preenche com valores iniciais
    dataTable = {}
    dataTable["battery_level"] = "1.0"

    #E tambem cria o arquivo e preenche com as informacoes contidas no dicionario acima (em string para evitar problemas com json)
    dataFile = open("vehicle_data.json", "w")
    json.dump(dataTable, dataFile)
    dataFile.close()

#Carrega as informacoes gravadas (ID)
idFile = open("ID.txt", "r")
vehicle_ID = idFile.read()
idFile.close()

#Carrega as informacoes gravadas (vehicle_data)
dataFile = open("vehicle_data.json", "w")
loadedTable = json.load(dataFile)
dataFile.close()

#Modifica as informacoes do objeto do veiculo
vehicle.ID = vehicle_ID
vehicle.battery_level = loadedTable["battery_level"]

#Print de teste
print(vehicle.ID)
print(vehicle.battery_level)