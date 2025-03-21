#Importa bibliotecas basicas do python 3
import string
import random
import socket
import json

#Importa as bibliotecas customizadas da aplicacao
from lib.db import *

#Classe do servidor
class Server():
    
    #Funcao inicializadora da classe
    def __init__(self):

        #Atributos
        self.randomID = ""
        self.requestLog = {}

    #Obtem o um novo ID aleatorio
    def getRandomID(self, actualRandom):

        lettersanddigits = string.ascii_uppercase + string.digits

        #Loop para gerar IDs ate satisfazer certas condicoes
        while True:

            randomID = ""

            #Concatena os os digitos ou letras aleatorios para um novo ID
            for count in range(0,24):
                randomID += random.choice(lettersanddigits)

            #Concatena com ".json" para saber qual e o nome do arquivo a ser analisado
            completeFileName = (randomID + ".json")
            
            #Caso o arquivo esperado nao exista
            if ((verifyFile(["clientdata", "clients"], completeFileName) == False) and (randomID != actualRandom)):
                
                #Retorna o novo ID aleatorio
                return randomID

    #Funcao para receber uma requisicao
    def listenToRequest(self):

        #Cria o soquete, torna a conexao reciclavel, reserva a porta local 8001 para a conexao e liga o modo de escuta        
        socket_receiver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_receiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket_receiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        socket_receiver.bind((socket.gethostbyname(socket.gethostname()), 8001))
        socket_receiver.listen(2)

        #Valores iniciais da mensagem de requisicao (mensagem vazia)
        msg = bytes([])
        add = ""
        
        try:
            #Espera a mensagem pelo tempo estipulado no timeout
            conn, add = socket_receiver.accept()
            msg = conn.recv(1024)
        except:
            pass
        
        #Fecha a conexao (desfaz o soquete)
        socket_receiver.close()
        
        #Decodifica a mensagem (a qual foi enviada em formato "bytes", codec "UTF-8")
        decodedBytes = msg.decode('UTF-8')
        
        #Se uma resposta valida foi recebida, a mensagem nao deve ser vazia
        if (len(decodedBytes) > 0):

            print("=============================================")
            print(add)
            print(msg)
            print(decodedBytes)
            print("=============================================")

            #De-serializa a mensagem decodificada 
            unserializedObj = json.loads(decodedBytes)

            #Retorna o objeto da mensagem
            return (add, unserializedObj)
        
        #Retorna atributos de uma mensagem nao-recebida ou vazia
        return (add, "")
    
    #Funcao para enviar uma resposta de volta ao cliente
    def sendResponse(self, clientAddress, response):

        #Cria o soquete e torna a conexao reciclavel
        socket_sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_sender.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket_sender.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        #Obtem a string do endereco do cliente
        clientAddressString, _ = clientAddress

        #Serializa a requisicao utilizando json
        serializedResponse = json.dumps(response)

        print("--------------------------------------------")
        print(clientAddress)
        print(clientAddressString)
        print(serializedResponse)
        print("--------------------------------------------")
        
        try:
            #Tenta fazer a conexao (endereco do cliente, porta 8002), envia a resposta em formato "bytes", codec "UTF-8", pela conexao
            socket_sender.connect((clientAddressString, 8002))
            socket_sender.send(bytes(serializedResponse, 'UTF-8'))
        except Exception as err:
            print(err)

        #Fecha a conexao (desfaz o soquete)
        socket_sender.close()

    #Funcao para registrar uma estacao de recarga
    def registerChargeStation(self, requestID, stationAddress, randomID, requestParameters):
        
        stationAddressString = json.dumps(stationAddress)

        #Caso os parametros da requisicao sejam do tamanho adequado...
        if (len(requestParameters) >= 4):
            
            #...Recupera o ID da estacao
            stationID = requestParameters[0]

            #Caso o ID da estacao fornecido seja igual ao ID aleatorio atual esperado
            if (stationID == randomID):
                
                #Cria o dicionario das informacoes e preenche com as informacoes passadas como parametros da requisicao
                stationInfo = {}
                stationInfo["coordinates"] = requestParameters[1]
                stationInfo["available_spots"] = requestParameters[2]
                stationInfo["unitary_price"] = requestParameters[3]
                
                #Concatena o nome do arquivo
                fileName = (randomID + ".json")

                #Grava as informacoes em arquivo de texto
                createFile(["clientdata", "clients", fileName], stationInfo)

                self.requestLog[stationAddressString] = [requestID, 'OK']
                self.sendResponse(stationAddress, 'OK')

                #Gera um novo ID aleatorio e exibe mensagem para conhecimento do mesmo
                newRandomID = self.getRandomID(randomID)
                print("ID para o proximo cadastro de estacao de carga: " + newRandomID)
                return newRandomID
        
        else:

            self.requestLog[stationAddressString] = [requestID, 'ERR']
            self.sendResponse(stationAddress, 'ERR')

    #Funcao para registrar novo veiculo
    def registerVehicle(self, requestID, vehicleAddress, randomID):

        vehicleAddressString = json.dumps(vehicleAddress)
        self.requestLog[vehicleAddressString] = [requestID, randomID]
        self.sendResponse(vehicleAddress, self.getRandomID(randomID))
        

#Programa inicia aqui
#Cria um objeto da classe Server
localServer = Server()

#Obtem um ID aleatorio de 24 elementos alfanumericos e exibe mensagem da operacao
localServer.randomID = localServer.getRandomID("*")
print("ID para o proximo cadastro de estacao de carga: " + localServer.randomID)

#Loop do programa
while True:
    
    #Espera chegar uma requisicao
    clientAddress, requestInfo = localServer.listenToRequest()
    
    #Gera uma string do endereco, de modo a gerenciar as requisicoes
    clientAddressString = json.dumps(clientAddress)

    #Se o tamamanho da lista de requisicao for adequado
    if (len(requestInfo) >= 4):
        
        #Recupera as informacoes da lista de requisicao
        clientID = requestInfo[0]
        requestID = requestInfo[1]
        requestName = requestInfo[2]
        requestParameters = requestInfo[3]

        #Verifica se a requisicao atual e uma nova requisicao ou uma repeticao de requisicao ja feita (o que e esperado caso clientes nao recebam resposta de sua requisicao)
        if (((clientAddressString in localServer.requestLog) == False) or (localServer.requestLog[clientAddressString][0] != requestID)):
            
            #Executa diferente requisicoes dependendo do nome da requisicao (acronimo)
            if (requestName == 'rcs'):
                localServer.registerChargeStation(requestID, clientAddress, localServer.randomID, requestParameters)
            if (requestName == 'rve'):
                localServer.registerVehicle(requestID, clientAddress, localServer.randomID)

        #Caso contrario, manda a resposta novamente
        else:

            localServer.sendResponse(clientAddress, localServer.requestLog[clientAddressString][1])

    #Caso contrario, se o endereco do cliente nao for vazios
    elif clientAddress != "":
            
            #Response que a requisicao e invalida
            localServer.sendResponse(clientAddress, 'ERR')