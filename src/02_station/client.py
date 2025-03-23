#Importa bibliotecas basicas do python 3
import json
import socket

#Importa as bibliotecas customizadas da aplicacao
from lib.db import *
from lib.io import *

#Classe do usuario
class Station():
    
    #Funcao inicializadora da classe
    def __init__(self):
        
        #Atributos
        self.ID = ""
        self.unitary_price = 0
        self.available_slots = 0

    #Funcao para receber uma resposta de requisicao
    def receiveFromServer(self):

        #Cria o soquete, torna a conexao reciclavel, estabelece um timeout (2 segundos), reserva a porta local 8002 para a conexao e liga o modo de escuta
        socket_receiver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_receiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket_receiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        socket_receiver.settimeout(10.0)
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
    
    #Funcao para enviar uma requisicao ao servidor
    def sendToServer(self, serverName, request):

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
    
    #Funcao para registrar a estacao
    def registerStation(self, requestID, coord_x, coord_y, unitary_price, available_slots):
        
        #ID da estacao
        stationID = input("ID para a estacao de carga (como fornecido pelo servidor): ")

        #Parametros da requisicao
        requestParameters = [stationID, coord_x, coord_y, unitary_price, available_slots]

        #Formula o conteudo da requisicao a ser enviada
        #O conteudo e uma lista de ao menos 4 elementos (ID de quem requeriu, ID da requisicao, nome da requisicao e parametros da mesma)
        requestContent = ['', requestID, 'rcs', requestParameters]
        
        #Envia a requisicao para o servidor da aplicacao
        self.sendToServer('charge_server', requestContent)

        #Espera a resposta
        (add, response) = self.receiveFromServer()

        #Se a resposta nao for adequada ("OK")...
        while (response != "OK"):
            
            #ID da estacao
            stationID = input("ID para a estacao de carga (como fornecido pelo servidor): ")

            #Parametros da requisicao
            requestParameters = [stationID, coord_x, coord_y, unitary_price, available_slots]

            #Formula o conteudo da requisicao a ser enviada
            #O conteudo e uma lista de ao menos 4 elementos (ID de quem requeriu, ID da requisicao, nome da requisicao e parametros da mesma)
            requestContent = ['', requestID, 'rcs', requestParameters]
            
            #Envia a requisicao para o servidor da aplicacao
            self.sendToServer('charge_server', requestContent)

            #Espera a resposta
            (add, response) = self.receiveFromServer()

            #Muda o ID da requisicao (para controle por parte do servidor do que ja foi executado)
            if (int(requestID) < 63):
                requestID = str(int(requestID) + 1)
            else:
                requestID = "1"

        #Muda o ID da requisicao (para controle por parte do servidor do que ja foi executado)
        if (int(requestID) < 63):
            requestID = str(int(requestID) + 1)
        else:
            requestID = "1"

        #Retorna a resposta (ID da estacao)
        return stationID

#Programa inicia aqui
#Cria um objeto da classe User
station = Station()

#Valores iniciais do programa
requestID = "0"

#Cria um dicionario dos atributos da estacao
dataTable = {}

#Verifica se o arquivo de texto "ID.txt" esta presente, e caso nao esteja...
if (verifyFile(["stationdata"], "ID.txt") == False):

    #Valores dos pares chave-valor sao sempre string para evitar problemas com json
    dataTable["coord_x"] = str(enterNumber("Coordenada x do posto de recarga: ", "ENTRADA INVALIDA."))
    dataTable["coord_y"] = str(enterNumber("Coordenada y do posto de recarga: ", "ENTRADA INVALIDA."))
    dataTable["unitary_price"] = str(enterNumber("Preco unitario do Wh, em BRL: ", "ENTRADA INVALIDA."))
    dataTable["available_slots"] = str(enterInt("Quantidade de pontos de carga disponiveis no local: ", "ENTRADA INVALIDA."))

    #ID da estacaodataTable["coord_x"]
    stationID = station.registerStation(requestID, dataTable["coord_x"], dataTable["coord_y"], dataTable["unitary_price"], dataTable["available_slots"])
    
    #Cria um novo arquivo
    createFile(["stationdata", "ID.txt"], stationID)

#Verifica se o arquivo de texto "station_data.json" esta presente, e caso nao esteja...
if (verifyFile(["stationdata"], "station_data.json") == False):

    #E tambem cria o arquivo e preenche com as informacoes contidas no dicionario acima
    createFile(["stationdata", "station_data.json"], dataTable)

#Carrega as informacoes gravadas (ID)
station.ID = readFile(["stationdata", "ID.txt"])

#Carrega as informacoes gravadas (station_data)
loadedTable = readFile(["stationdata", "station_data.json"])

#Modifica as informacoes do objeto da estacao
station.available_slots = int(loadedTable["available_slots"])
station.unitary_price = float(loadedTable["unitary_price"])

#Print de teste
print("*********************************************")
print(station.ID)
print(station.available_slots)
print(station.unitary_price)
print("*********************************************")