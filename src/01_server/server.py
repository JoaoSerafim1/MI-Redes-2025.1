#Importa bibliotecas basicas do python 3
import string
import random
import socket
import json

#Importa as bibliotecas customizadas da aplicacao
from lib.db import *
from lib.mf import *
from lib.pr import *

#Classe do servidor
class Server():
    
    #Funcao inicializadora da classe
    def __init__(self):

        #Atributos
        self.randomID = ""

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
            if ((verifyFile(["clientdata", "clients", "stations"], completeFileName) == False) and (verifyFile(["clientdata", "clients", "vehicles"], completeFileName) == False) and (randomID != actualRandom)):
                
                #Retorna o novo ID aleatorio
                return randomID

    #Funcao para receber uma requisicao
    def listenToRequest(self, timeout):

        #Cria o soquete, torna a conexao reciclavel, reserva a porta local 8001 para a conexao e liga o modo de escuta        
        socket_receiver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_receiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket_receiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        if (timeout != 0):
            socket_receiver.settimeout(timeout)

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

    #Funcao para fazer entrada de requisicao processada
    def registerRequestResult(self, clientAddress, requestID, requestResult):
        
        #Dicionario de propriedades da requisicao
        requestTable = {}
        requestTable["ID"] = requestID
        requestTable["result"] = requestResult

        #Obtem a string de endereco do cliente
        clientAddressString, _ = clientAddress

        #Concatena o nome do arquivo para a entrada da requisicao
        requestFileName = (clientAddressString.strip('.') + ".json")

        #Cria uma entrada referente a requisicao e ao resultado obtido
        createFile(["clientdata", "requests", requestFileName], requestTable)

    #Funcao para registrar uma estacao de recarga
    def registerChargeStation(self, requestID, stationAddress, randomID, requestParameters):

        #Caso os parametros da requisicao sejam do tamanho adequado...
        if (len(requestParameters) >= 4):

            #...Recupera o ID da estacao
            stationID = requestParameters[0]

            #Caso o ID da estacao fornecido seja igual ao ID aleatorio atual esperado
            if (stationID == randomID):

                #Cria o dicionario das informacoes e preenche com as informacoes passadas como parametros da requisicao
                stationInfo = {}
                stationInfo["coord_x"] = requestParameters[1]
                stationInfo["coord_y"] = requestParameters[2]
                stationInfo["unitary_price"] = requestParameters[3]
                stationInfo["actual_vehicle"] = ""
                stationInfo["station_address"] = stationAddress
                
                #Concatena o nome do arquivo/
                fileName = (randomID + ".json")

                #Grava as informacoes em arquivo de texto
                createFile(["clientdata", "clients", "stations", fileName], stationInfo)
                
                #Grava o status da requisicao (mesmo conteudo da mensagem enviada como resposta)
                self.registerRequestResult(stationAddress, requestID, 'OK')

                #Responde o status da requisicao para o cliente
                self.sendResponse(stationAddress, 'OK')

                #Gera um novo ID aleatorio e exibe mensagem para conhecimento do mesmo
                newRandomID = self.getRandomID(randomID)
                print("ID para o proximo cadastro de estacao de carga: " + newRandomID)
                return newRandomID
            
            else:

                #Grava o status da requisicao (mesmo conteudo da mensagem enviada como resposta)
                self.registerRequestResult(stationAddress, requestID, 'ERR')

                #Responde o status da requisicao para o cliente
                self.sendResponse(stationAddress, 'ERR')
        
        else:

            #Grava o status da requisicao (mesmo conteudo da mensagem enviada como resposta)
            self.registerRequestResult(stationAddress, requestID, 'ERR')

            #Responde o status da requisicao para o cliente
            self.sendResponse(stationAddress, 'ERR')

    #Funcao para registrar novo veiculo
    def registerVehicle(self, requestID, vehicleAddress, randomID):

        #Obtem um ID aleatorio para o veiculo
        vehicleRandomID = self.getRandomID(randomID)

        #Concatena a string do nome do arquivo do veiculo
        vehicleFileName = (vehicleRandomID + ".json")

        #...cria um dicionario dos atributos do veiculo e preenche com valores iniciais
        #Valores dos pares chave-valor sao sempre string para evitar problemas com json
        dataTable = {}
        dataTable["purchases"] = []

        #Cria um novo arquivo para o veiculo
        createFile(["clientdata", "clients", "vehicles", vehicleFileName], dataTable)

        #Grava o status da requisicao (mesmo conteudo da mensagem enviada como resposta)
        self.registerRequestResult(vehicleAddress, requestID, vehicleRandomID)

        #Responde o status da requisicao para o cliente
        self.sendResponse(vehicleAddress, vehicleRandomID)

    #Funcao para retornar a distancia ate o posto de recarga mais proximo e seu ID
    def respondWithDistance(self, requestID, vehicleAddress, requestParameters):
        
        #Informacoes iniciais da mensagem de resposta
        IDToReturn = "0"
        distanceToReturn = 0
        unitaryPriceToReturn = "0"
        stationList = listFiles(["clientdata", "clients", "stations"])

        for stationIndex in range(0, len(stationList)):
            
            actualStationFileName = stationList[stationIndex]
            actualID = ""
            
            for IDIndex in range(0, 24):

                actualID += actualStationFileName[IDIndex]

            actualStationTable = readFile(["clientdata", "clients", "stations", actualStationFileName])
            
            actualVehicle = int(actualStationTable["actual_vehicle"])

            actualDistance = getDistance(requestParameters[0], requestParameters[1], float(actualStationTable["coord_x"]), float(actualStationTable["coord_y"]))

            if ((actualVehicle == "") and ((stationIndex == 0) or (actualDistance < distanceToReturn))):

                distanceToReturn = actualDistance
                unitaryPriceToReturn = actualStationTable["unitary_price"]

        #Grava o status da requisicao (mesmo conteudo da mensagem enviada como resposta)
        self.registerRequestResult(vehicleAddress, requestID, [IDToReturn, str(distanceToReturn), unitaryPriceToReturn])

        #Responde o status da requisicao para o cliente
        self.sendResponse(vehicleAddress, [IDToReturn, str(distanceToReturn), unitaryPriceToReturn])

    #Funcao para registrar uma estacao de recarga
    def attemptCharge(self, requestID, vehicleAddress, requestParameters):

        #Caso os parametros da requisicao sejam do tamanho adequado...
        if (len(requestParameters) >= 4):

            #Recupera as informacoes
            purchaseID = requestParameters[0]
            vehicleID = requestParameters[1]
            stationID = requestParameters[2]
            paidAmmount = requestParameters[3]

            #Nome do arquivo do veiculo de carga a ser analizado
            vehicleFileName = (vehicleID + ".json")
            #Nome do arquivo da estacao de carga a ser analizado
            stationFileName = (stationID + ".json")

            #Caso o ID do veiculo/estacao fornecidos sejam validos e a compra seja confirmada
            if ((verifyFile(["clientdata", "clients", "vehicles"], vehicleFileName) == True) and (verifyFile(["clientdata", "clients", "stations"], stationFileName) == True) and confirmPurchase(purchaseID) == True):

                #Carrega o dicionario de informacoes da estacao
                stationInfo = readFile(["clientdata", "clients", "stations", stationFileName])

                #Caso o ponto de carga esteja disponivel para a operacao
                if (stationInfo["actual_vehicle"] == ""):

                    #Nome do arquivo da compra
                    purchaseFileName = (purchaseID + ".json")

                    #Cria um dicionario das informacoes da compra, adiciona informacoes e grava um arquivo
                    purchaseTable = {}
                    purchaseTable["vehicle_ID"] = vehicleID
                    purchaseTable["station_ID"] = stationID
                    purchaseTable["total"] = paidAmmount
                    purchaseTable["unitary_price"] = stationInfo["unitary_price"]
                    createFile(["clientdata", "purchases", purchaseFileName])

                    #Carrega o dicionario de informacoes do veiculo, Adiciona a compra a lista de compras do veiculo (cliente) e grava o resultado
                    vehicleInfo = readFile(["clientdata", "clients", "vehicles", vehicleFileName])
                    vehicleInfo["purchases"].append(purchaseID)
                    createFile(["clientdata", "clients", "vehicles", vehicleFileName], vehicleInfo)

                    #Modifica o veiculo atual na estacao de carga e grava o resultado
                    stationInfo["actual_vehicle"] = vehicleID
                    createFile(["clientdata", "clients", "stations", stationFileName], stationInfo)

                    #Grava o status da requisicao (mesmo conteudo da mensagem enviada como resposta)
                    self.registerRequestResult(vehicleAddress, requestID, 'OK')

                    #Envia mensagem a estacao de carga
                    self.sendResponse(stationInfo["station_address"], vehicleID)

                    #Espera resposta da estacao de carga
                    (_, response) = self.listenToRequest(5)

                    #Enquanto nao for o esperado
                    while (response != "OK"):

                        #Envia mensagem a estacao de carga
                        self.sendResponse(stationInfo["station_address"], vehicleID)

                        #Espera resposta da estacao de carga
                        (_, response) = self.listenToRequest(5)
                    
                    #Envia mensagem de resposta ao veiculo
                    self.sendResponse(vehicleAddress, 'OK')

                else:
                    
                    #Caso contrario (slot de carga ocupado durante a compra), cancela a compra
                    cancelPurchase(purchaseID)

                    #Grava o status da requisicao (mesmo conteudo da mensagem enviada como resposta)
                    self.registerRequestResult(vehicleAddress, requestID, 'ERR')

                    #Envia mensagem de resposta ao veiculo
                    self.sendResponse(vehicleAddress, 'ERR')

            else:

                #Grava o status da requisicao (mesmo conteudo da mensagem enviada como resposta)
                self.registerRequestResult(vehicleAddress, requestID, 'ERR')

                #Responde o status da requisicao para o cliente
                self.sendResponse(vehicleAddress, 'ERR')

        else:

            #Grava o status da requisicao (mesmo conteudo da mensagem enviada como resposta)
            self.registerRequestResult(vehicleAddress, requestID, 'ERR')

            #Responde o status da requisicao para o cliente
            self.sendResponse(vehicleAddress, 'ERR')


#Inicio do programa
#Cria um objeto da classe Server
localServer = Server()

#Obtem um ID aleatorio de 24 elementos alfanumericos e exibe mensagem da operacao
localServer.randomID = localServer.getRandomID("*")
print("ID para o proximo cadastro de estacao de carga: " + localServer.randomID)

#Loop do programa
while True:
    
    #Espera chegar uma requisicao
    clientAddress, requestInfo = localServer.listenToRequest(0)

    #Se o tamamanho da lista de requisicao for adequado
    if (len(requestInfo) >= 4):
        
        #Recupera as informacoes da lista de requisicao
        clientID = requestInfo[0]
        requestID = requestInfo[1]
        requestName = requestInfo[2]
        requestParameters = requestInfo[3]

        #Obtem a string de endereco do cliente
        clientAddressString, _ = clientAddress

        #Concatena o nome do arquivo para a entrada da requisicao
        requestFileName = (clientAddressString.strip('.') + ".json")

        #Cria uma entrada referente a requisicao e ao resultado obtido
        #createFile(["clientdata", "requests", requestFileName], requestTable)

        #Variavel que diz se a requisicao sera executada
        willExecute = True

        #Resultado da requisicao, inicialmente vazio
        requestResult = ""
        
        #Verifica se a requisicao atual tem ID diferente de 0 e se vem de um endereco que ja fez requisicoes
        if ((requestID != "0" ) and (verifyFile(["clientdata", "requests"], requestFileName) == True)):
            
            #Recupera informacoes da ultima requisicao
            requestTable = readFile(["clientdata", "requests", requestFileName])
            storedRequestID = requestTable["ID"]
            requestResult = requestTable["result"]

            #Verifica se o ID da ultima requisicao e o mesmo da atual
            if(requestID == storedRequestID):

                #Se for, nao sera executada requisicao
                willExecute = False
        
        #Caso a intencao de execucao da requisicao ainda estiver de pe
        if (willExecute == True):
            
            #Executa diferente requisicoes dependendo do nome da requisicao (acronimo)
            if (requestName == 'rcs'):
                localServer.registerChargeStation(requestID, clientAddress, localServer.randomID, requestParameters)
            if (requestName == 'rve'):
                localServer.registerVehicle(requestID, clientAddress, localServer.randomID)

        #Caso contrario, manda a resposta novamente
        else:

            localServer.sendResponse(clientAddress, requestResult)

    #Caso contrario e se o endereco do cliente nao for vazio
    elif clientAddress != "":
        
        #Response que a requisicao e invalida
        localServer.sendResponse(clientAddress, 'ERR')