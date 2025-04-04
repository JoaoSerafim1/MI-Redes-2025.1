#Importa bibliotecas basicas do python 3
import json
import socket
import threading

#Importa as bibliotecas customizadas da aplicacao
from lib.db import *
from lib.io import *
from lib.pr import *

#Importa customTkinter
import customtkinter as ctk


#Classe do usuario
class User():
    
    #Funcao inicializadora da classe
    def __init__(self):
        
        #Atributos
        self.ID = ""
        self.battery_level = ""
        self.capacity = ""
        self.vehicle = ""
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

        #print("--------------------------------------------")
        #print(serverName)
        #print(SERVER)
        #print(serializedRequest)
        #print("--------------------------------------------")
        
        try:
            #Tenta fazer a conexao (endereco do servidor, porta 8001), envia a requisicao em formato "bytes", codec "UTF-8", pela conexao
            socket_sender.connect((SERVER, 8001))
            socket_sender.send(bytes(serializedRequest, 'UTF-8'))
        except:
            pass

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

            #print("=============================================")
            #print(add)
            #print(msg)
            #print(decodedBytes)
            #print("=============================================")

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
    
    def nearestSpotRequest(self, requestID): #solicita distancia do posto mais proximo
        
        global nearestStationID
        global nearestStationDistance
        global nearestStationPrice

        localDataTable = readFile(["vehicledata", "vehicle_data.json"])
        
        requestParameters = [localDataTable["coord_x"],localDataTable["coord_y"]]
        requestContent = [requestID, 'nsr', requestParameters]
        self.sendRequest('charge_server', requestContent)
        (add, response) = self.listenToResponse()

        if (int(requestID) < 63):
            requestID = str(int(requestID) + 1)
        else:
            requestID = "0"

        if (len(response) < 1):
            
            nearestStationID = ""
            nearestStationDistance = "SERVIDOR INDISPONÍVEL"
            nearestStationPrice = ""
        
        elif (response[0] == "0"):
            
            nearestStationID = ""
            nearestStationDistance = "NENHUMA ESTAÇÃO DISPONÍVEL ENCONTRADA"
            nearestStationPrice = ""
        
        else:
            
            nearestStationID = response[0]
            nearestStationDistance = (" " + str(response[1]) + " Km ")
            nearestStationPrice = response[2]
    
    def simulateForNearestSpot(self, requestID): #Obtem as informacoes de compra

        global nearestStationID
        global nearestStationPrice

        global nextPurchaseID
        global nextAmountToPay
        
        if((float(self.battery_level) < 1) and (nearestStationID != "")):
            
            nextPurchaseID, nextAmountToPay = simulatePayment(self.capacity, self.battery_level, nearestStationPrice)

    def payForNearestSpot(self, requestID): #reserva posto

        global nearestStationID

        global nextPurchaseID
        global nextAmountToPay
        global purchaseResult

        if((float(self.battery_level) < 1) and (nearestStationID != "") and (confirmPayment(nextPurchaseID) == True)):
            
            requestParameters = [nextPurchaseID, self.ID, nearestStationID, nextAmountToPay]
            requestContent = [requestID, 'bcs', requestParameters]

            self.sendRequest('charge_server', requestContent)
            (add, response) = self.listenToResponse()

            while(response == ""):

                self.sendRequest('charge_server', requestContent)
                (add, response) = self.listenToResponse()

            if(response == "OK"):
                purchaseResult = "Ponto reservado. Espere de 1 a 2 minutos para comecar o processo de recarga."
            else:
                purchaseResult = "O local está reservado ou é inválido. Sua compra foi estornada automaticamente."

            if (int(requestID) < 63):
                requestID = str(int(requestID) + 1)
            else:
                requestID = "0"

            nextPurchaseID = ""
    

def infoUpdate():

    while True:

        #Carrega as informacoes gravadas (vehicle_data)
        loadedTable = readFile(["vehicledata", "vehicle_data.json"])

        #Modifica as informacoes do objeto do veiculo
        vehicle.battery_level = loadedTable["battery_level"]
        vehicle.capacity = loadedTable["capacity"]

        battery_info_text.set(" Carga: " + str(float(vehicle.battery_level) * 100) + "% => " + str(float(vehicle.capacity) * float(vehicle.battery_level)) + "/" + str(vehicle.capacity) + " KWh ")
        if (float(vehicle.battery_level) < 0.3):
            critical_battery_text.set(" BATERIA EM NÍVEL CRÍTICO! ")
        else:
            critical_battery_text.set(" BATERIA NORMAL ")
        
        distance_info_text.set(str(nearestStationDistance))

        if(len(nextPurchaseID) > 0):
            next_purchase_info_text.set(" UUID da compra: " + nextPurchaseID + " / TOTAL: " + nextAmountToPay + " ")
        else:
            next_purchase_info_text.set(" Não existe compra esperando confirmação. ")

        next_purchase_result_text.set(purchaseResult)


#Programa inicia aqui
#Cria um objeto da classe User
vehicle = User()

#Valores iniciais do programa
requestID = "0"
nearestStationID = ""
nearestStationDistance = ""
nearestStationPrice = ""

nextPurchaseID = ""
nextAmountToPay = ""

purchaseResult = ""

#Cria um dicionario dos atributos do veiculo
dataTable = {}


#Verifica se o arquivo de texto "ID.txt" esta presente, e caso nao esteja...
if (verifyFile(["vehicledata"], "ID.txt") == False):
    
    #Cria um novo arquivo
    writeFile(["vehicledata", "ID.txt"], vehicle.registerVehicle(requestID))

#Verifica se o arquivo de texto "vehicle_data.json" esta presente, e caso nao esteja...
if (verifyFile(["vehicledata"], "vehicle_data.json") == False):
    
    #Valores dos pares chave-valor sao sempre string para evitar problemas com json
    dataTable["capacity"] = str(enterNumber("Capacidade atual de carga do veiculo, em KWh: ", "ENTRADA INVALIDA."))
    dataTable["battery_level"] = "1.0"
    dataTable["coord_x"] = "1.0"
    dataTable["coord_y"] = "1.0"

    #E tambem cria o arquivo e preenche com as informacoes contidas no dicionario acima
    writeFile(["vehicledata", "vehicle_data.json"], dataTable)

#Carrega as informacoes gravadas (ID)
vehicle.ID = readFile(["vehicledata", "ID.txt"])

frame = ctk.CTk()
frame._set_appearance_mode('dark')
frame.title('Cliente')
frame.geometry('400x600')

userID = ctk.CTkLabel(frame,text=(" " + vehicle.ID + " "))
userID.pack(pady=10)

battery_info_text = ctk.StringVar()
battery_info = ctk.CTkLabel(frame,textvariable=battery_info_text)
battery_info.pack(pady=10)

critical_battery_text = ctk.StringVar()
critical_battery = ctk.CTkLabel(frame,textvariable=critical_battery_text)
critical_battery.pack(pady=5)

spotRequestButton = ctk.CTkButton(frame,text=' Obter a distância até a estação de recarga mais próxima ',command=lambda:vehicle.nearestSpotRequest(requestID))
spotRequestButton.pack(pady=10)

distance_info_text = ctk.StringVar()
distance_info = ctk.CTkLabel(frame,textvariable=distance_info_text)
distance_info.pack(pady=5)

simulatePayButton = ctk.CTkButton(frame,text=' Gerar guia de pagamento ',command=lambda:vehicle.simulateForNearestSpot(requestID))
simulatePayButton.pack(pady=10)

next_purchase_info_text = ctk.StringVar()
next_purchase_info = ctk.CTkLabel(frame,textvariable=next_purchase_info_text)
next_purchase_info.pack(pady=5)

bookButton = ctk.CTkButton(frame,text=' Recarregar totalmente na estação mais próxima ',command=lambda:vehicle.payForNearestSpot(requestID))
bookButton.pack(pady=10)

next_purchase_result_text = ctk.StringVar()
next_purchase_result = ctk.CTkLabel(frame,textvariable=next_purchase_result_text)
next_purchase_result.pack(pady=5)

newThread = threading.Thread(target=infoUpdate, args=())
newThread.start()

frame.mainloop()