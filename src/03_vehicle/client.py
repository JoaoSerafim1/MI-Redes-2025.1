#Importa bibliotecas basicas do python 3
import json
import socket

#Importa as bibliotecas customizadas da aplicacao
from lib.db import *
from lib.io import *

#Classe do usuario
class User():
    
    #Funcao inicializadora da classe
    def __init__(self):
        
        #Atributos
        self.ID = ""
        self.user = ""
        self.battery_level = ""
        self.vehicle = ""
        self.payment_method = ""
        self.payment_history = {}
    
    #Funcao para enviar uma requisicao ao servidor
    def sendRequest(self, serverName, request):

        #Cria o soquete e torna a conexao reciclavel
        socket_sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_sender.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket_sender.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        #Obtem o endereco do servidor com base em seu nome
        SERVER = socket.gethostbyname(serverName)

        #Serializa a requisicao utilizando json
        serializedRequest = json.dumps(request)

        print("--------------------------------------------")
        print(serverName)
        print(SERVER)
        print(serializedRequest)
        print("--------------------------------------------")
        
        try:
            #Tenta fazer a conexao (endereco do servidor, porta 8001), envia a requisicao em formato "bytes", codec "UTF-8", pela conexao
            socket_sender.connect((SERVER, 8001))
            socket_sender.send(bytes(serializedRequest, 'UTF-8'))
        except Exception as err:
            print(err)

        #Fecha a conexao (desfaz o soquete)
        socket_sender.close()

    #Funcao para receber uma resposta de requisicao
    def listenToResponse(self):

        #Cria o soquete, torna a conexao reciclavel, estabelece um timeout (2 segundos), reserva a porta local 8002 para a conexao e liga o modo de escuta
        socket_receiver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_receiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket_receiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        socket_receiver.settimeout(2.0)
        socket_receiver.bind((socket.gethostbyname(socket.gethostname()), 8002))
        socket_receiver.listen(2)

        #Valores iniciais da mensagem de resposta (mensagem vazia)
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
    
    #Funcao para registrar o veiculo
    def registerVehicle(self, requestID):
        
        #Formula o conteudo da requisicao a ser enviada
        #O conteudo e uma lista de ao menos 4 elementos (ID de quem requeriu, ID da requisicao, nome da requisicao e parametros da mesma)
        requestContent = [requestID, 'rve', '']
        
        #Envia a requisicao para o servidor da aplicacao
        self.sendRequest('charge_server', requestContent)

        #Espera a resposta
        (add, response) = self.listenToResponse()

        #Se a resposta nao for adequada (string de 24 caracteres alfanumericos)...
        while (len(response) != 24):
            
            #Envia novamente a requisicao e espera a resposta
            self.sendRequest('charge_server', requestContent)

            (add, response) = self.listenToResponse()

        #Muda o ID da requisicao (para controle por parte do servidor do que ja foi executado)
        if (int(requestID) < 63):
            requestID = str(int(requestID) + 1)
        else:
            requestID = "1"

        #Retorna a resposta (ID do veiculo)
        return response

    def batteryCheck(self): #notifica se a bateria esta em estado critico
        if self.battery_level < 0.3:
            return 1
        return 0
    
    def bookChargeSpot(self, requestID): #reserva posto

        requestContent = [requestID, 'bcs', '']
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
        
        requestContent = [requestID, 'nsr', '']
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

#Cria um dicionario dos atributos do veiculo
dataTable = {}


#Verifica se o arquivo de texto "ID.txt" esta presente, e caso nao esteja...
if (verifyFile(["vehicledata"], "ID.txt") == False):
    
    #Cria um novo arquivo
    writeFile(["vehicledata", "ID.txt"], vehicle.registerVehicle(requestID))

#Verifica se o arquivo de texto "vehicle_data.json" esta presente, e caso nao esteja...
if (verifyFile(["vehicledata"], "vehicle_data.json") == False):
    
    #Valores dos pares chave-valor sao sempre string para evitar problemas com json
    dataTable["capacity"] = str(enterNumber("Capacidade atual de carga do veiculo, em Wh: ", "ENTRADA INVALIDA."))
    dataTable["battery_level"] = "1.0"
    dataTable["coord_x"] = "1.0"
    dataTable["coord_y"] = "1.0"

    #E tambem cria o arquivo e preenche com as informacoes contidas no dicionario acima
    writeFile(["vehicledata", "vehicle_data.json"], dataTable)

#Carrega as informacoes gravadas (ID)
vehicle.ID = readFile(["vehicledata", "ID.txt"])

#Carrega as informacoes gravadas (vehicle_data)
loadedTable = readFile(["vehicledata", "vehicle_data.json"])

#Modifica as informacoes do objeto do veiculo
vehicle.battery_level = loadedTable["battery_level"]

#Print de teste
print("*********************************************")
print(vehicle.ID)
print(vehicle.battery_level)
print("*********************************************")