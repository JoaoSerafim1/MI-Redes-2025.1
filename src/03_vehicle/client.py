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
    def sendRequest(self, request):

        global serverAddress

        #Cria o soquete e torna a conexao reciclavel
        socket_sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_sender.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket_sender.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        #Obtem o endereco do servidor com base em seu nome
        #SERVER = socket.gethostbyname(serverName)

        #Serializa a requisicao utilizando json
        serializedRequest = json.dumps(request)

        #print("--------------------------------------------")
        #print(serverAddress)
        #print(serializedRequest)
        #print("--------------------------------------------")
        
        try:
            #Tenta fazer a conexao (endereco do servidor, porta 8001), envia a requisicao em formato "bytes", codec "UTF-8", pela conexao
            socket_sender.connect((serverAddress, 8001))
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
    def registerVehicle(self):
        
        global requestID

        #Garante que a criacao do veiculo so acontece uma vez
        #O servidor esta condicionado a executar requisicoes de indice 0 mesmo que a ultima requisicao para certo endereco tenha indice 0
        #Assim sendo, e preciso colocar um indice distinto de zero para forcar que isso nao aconteca
        #Entretanto, indices de 1 a 63 sao utilizados no ciclo normal de requisicao, entao o numero arbitrario aqui deve estar fora do intervalo
        #Caso contrario, poderia acontecer de o cliente nao conseguir registrar um novo veiculo no endereco, pois a ultima requisicao era do indice escolhido
        requestID = 64

        #Formula o conteudo da requisicao a ser enviada
        #O conteudo e uma lista de ao menos 4 elementos (ID de quem requeriu, ID da requisicao, nome da requisicao e parametros da mesma)
        requestContent = [requestID, 'rve', '']
        
        #Envia a requisicao para o servidor da aplicacao
        self.sendRequest(requestContent)

        #Espera a resposta
        (add, response) = self.listenToResponse()

        #Se a resposta nao for adequada (string de 24 caracteres alfanumericos)...
        while (len(response) != 24):
            
            #Envia novamente a requisicao e espera a resposta
            self.sendRequest(requestContent)

            (add, response) = self.listenToResponse()

        #Muda o ID da requisicao (para controle por parte do servidor do que ja foi executado)
        if (int(requestID) < 63):
            requestID = str(int(requestID) + 1)
        else:
            requestID = "1"

        #Retorna a resposta (ID do veiculo)
        return response
    
    #Solicita distancia do posto mais proximo
    def nearestSpotRequest(self):
        
        global requestID
        global nearestStationID
        global nearestStationDistance
        global nearestStationPrice

        #Le informacoes do veiculo
        localDataTable = readFile(["vehicledata", "vehicle_data.json"])
        
        #Confeccina o conteudo da requisicao e envia 1x
        requestParameters = [localDataTable["coord_x"],localDataTable["coord_y"]]
        requestContent = [requestID, 'nsr', requestParameters]
        self.sendRequest(requestContent)
        (add, response) = self.listenToResponse()

        #Atualiza o ID da requisicao
        if (int(requestID) < 63):
            requestID = str(int(requestID) + 1)
        else:
            requestID = "1"
        
        #Se nao receber resposta, o servidor esta indisponivel
        if (len(response) < 1):
            
            nearestStationID = ""
            nearestStationDistance = " SERVIDOR INDISPONÍVEL "
            nearestStationPrice = ""
        
        #Se receber resposta com campo do ID da estacao vazio, nenhum estacao foi encontrada (disponivel)
        elif (response[0] == "0"):
            
            nearestStationID = ""
            nearestStationDistance = " NENHUMA ESTAÇÃO DISPONÍVEL ENCONTRADA "
            nearestStationPrice = ""
        
        #Caso contrario, atualiza as informacoes de acordo com o retorno (informacoes da estacao mais proxima)
        else:
            
            nearestStationID = response[0]
            nearestStationDistance = response[1]
            nearestStationPrice = response[2]
    
    #Funca que gera a guia de pagamento para recarga
    def simulateForNearestSpot(self):

        global nearestStationID
        global nearestStationPrice

        global nextPurchaseID
        global nextAmountToPay
        
        #Se a bateria nao esta cheia e existe uma estacao para fazer a recarga, gera a guia de pagamento para encher a bateria
        if((float(self.battery_level) < 1) and (nearestStationID != "")):
            
            nextPurchaseID, nextAmountToPay = simulatePayment(self.capacity, self.battery_level, nearestStationPrice)

    #Funcao que efetua o pagamento da ultima guia gerada
    def payForNearestSpot(self):

        global requestID
        global nearestStationID

        global nextPurchaseID
        global nextAmountToPay
        global purchaseResult

        #Se a bateria nao esta cheia, existe uma estacao para fazer a recarga e o pagamento foi confirmado
        if((float(self.battery_level) < 1) and (nearestStationID != "") and (confirmPayment(nextPurchaseID) == True)):
            
            #Faz o conteudo da requisicao
            requestParameters = [nextPurchaseID, self.ID, nearestStationID, nextAmountToPay]
            requestContent = [requestID, 'bcs', requestParameters]

            #Envia a requisicao
            self.sendRequest(requestContent)
            (add, response) = self.listenToResponse()

            #Se nao receber resposta valida, repete o envio (so acontece caso o servidor esteja indisponivel)
            while(response == ""):

                self.sendRequest(requestContent)
                (add, response) = self.listenToResponse()

            #Exibe resultado da operacao
            if(response == "OK"):
                purchaseResult = (" Compra de UUID <" + nextPurchaseID + "> bem-sucedida. Espere de 1 a 2 minutos para comecar o processo de recarga. ")
            else:
                purchaseResult = " O local está reservado ou é inválido. Sua compra de UUID <" + nextPurchaseID + "> foi estornada automaticamente. "

            #Atualiza o ID de requisicao
            if (int(requestID) < 63):
                requestID = str(int(requestID) + 1)
            else:
                requestID = "1"

            #Zera o ID da proxima compra
            nextPurchaseID = ""
    
    #Funcao para obter informacoes da compra no indice a seguir
    def purchaseBackward(self):
        
        global requestID
        global purchaseHistoryIndex
        global displayPurchaseID
        global displayPurchaseTotal
        global displayPurchasePrice
        global displayPurchaseCharge

        #Faz o conteudo da requisicao (ID do veiculo e indice atual de compra - 1)
        requestParameters = [self.ID, str(int(purchaseHistoryIndex) - 1)]
        requestContent = [requestID, 'gpr', requestParameters]

        #Envia a requisicao
        self.sendRequest(requestContent)
        (add, response) = self.listenToResponse()

        #Se nao receber resposta valida, repete o envio (so acontece caso o servidor esteja indisponivel)
        while(response == ""):

            self.sendRequest(requestContent)
            (add, response) = self.listenToResponse()

        #Atualiza o ID de requisicao
        if (int(requestID) < 63):
            requestID = str(int(requestID) + 1)
        else:
            requestID = "1"

        #Caso a resposta diga que nao encontrou compra naquele indice para o veiculo
        if(response[0] == "0"):

            #Faz o conteudo da requisicao (ID do veiculo e indice atual de compra)
            requestParameters = [self.ID, str(purchaseHistoryIndex)]
            requestContent = [requestID, 'gpr', requestParameters]

            #Envia a requisicao
            self.sendRequest(requestContent)
            (add, response) = self.listenToResponse()

            #Se nao receber resposta valida, repete o envio (so acontece caso o servidor esteja indisponivel)
            while(response == ""):

                self.sendRequest(requestContent)
                (add, response) = self.listenToResponse()

            #Atualiza o ID de requisicao
            if (int(requestID) < 63):
                requestID = str(int(requestID) + 1)
            else:
                requestID = "1"

        #Caso contrario, atualiza o indice atual da compra analisada
        else:

            purchaseHistoryIndex = str(int(purchaseHistoryIndex) - 1)
        
        #Atualiza informacoes da compra exibida
        displayPurchaseID = response[0]
        displayPurchaseTotal = response[1]
        displayPurchasePrice = response[2]
        displayPurchaseCharge = response[3]
    
    #Funcao para obter informacoes da compra no indice a seguir
    def purchaseForward(self):
        
        global requestID
        global purchaseHistoryIndex
        global displayPurchaseID
        global displayPurchaseTotal
        global displayPurchasePrice
        global displayPurchaseCharge

        #Faz o conteudo da requisicao (ID do veiculo e indice atual de compra + 1)
        requestParameters = [self.ID, str(int(purchaseHistoryIndex) + 1)]
        requestContent = [requestID, 'gpr', requestParameters]

        #Envia a requisicao
        self.sendRequest(requestContent)
        (add, response) = self.listenToResponse()

        #Se nao receber resposta valida, repete o envio (so acontece caso o servidor esteja indisponivel)
        while(response == ""):

            self.sendRequest(requestContent)
            (add, response) = self.listenToResponse()

        #Atualiza o ID de requisicao
        if (int(requestID) < 63):
            requestID = str(int(requestID) + 1)
        else:
            requestID = "1"

        #Caso a resposta diga que nao encontrou compra naquele indice para o veiculo
        if(response[0] == "0"):

            #Faz o conteudo da requisicao (ID do veiculo e indice atual de compra)
            requestParameters = [self.ID, str(purchaseHistoryIndex)]
            requestContent = [requestID, 'gpr', requestParameters]

            #Envia a requisicao
            self.sendRequest(requestContent)
            (add, response) = self.listenToResponse()

            #Se nao receber resposta valida, repete o envio (so acontece caso o servidor esteja indisponivel)
            while(response == ""):

                self.sendRequest(requestContent)
                (add, response) = self.listenToResponse()

            #Atualiza o ID de requisicao
            if (int(requestID) < 63):
                requestID = str(int(requestID) + 1)
            else:
                requestID = "1"

        #Caso contrario, atualiza o indice atual da compra analisada
        else:

            purchaseHistoryIndex = str(int(purchaseHistoryIndex) + 1)
        
        #Atualiza informacoes da compra exibida
        displayPurchaseID = response[0]
        displayPurchaseTotal = response[1]
        displayPurchasePrice = response[2]
        displayPurchaseCharge = response[3]
    

#Funcao do thread que monitora mudancas nas informacoes guardadas no arquivo de dados do veiculo
def infoUpdate():

    while True:

        #Carrega as informacoes gravadas (vehicle_data)
        loadedTable = readFile(["vehicledata", "vehicle_data.json"])

        #Modifica as informacoes do objeto do veiculo
        vehicle.battery_level = loadedTable["battery_level"]
        vehicle.capacity = loadedTable["capacity"]

        #Atualiza label de texto do nivel da bateria e do aviso de bateria critica (menos de 30 porcento)
        battery_info_text.set(" Carga: " + str(float(vehicle.battery_level) * 100) + "% => " + str(float(vehicle.capacity) * float(vehicle.battery_level)) + "/" + str(vehicle.capacity) + " KWh ")
        if (float(vehicle.battery_level) < 0.3):
            critical_battery_text.set(" BATERIA EM NÍVEL CRÍTICO! ")
        else:
            critical_battery_text.set(" BATERIA NORMAL ")
        
        #Atualiza label de texto de informacao da distancia
        if (nearestStationID != ""):
            distance_info_text.set((" DISTANCIA: " + nearestStationDistance + " Km | Preço do KWh: " + nearestStationPrice + " "))
        else:
            distance_info_text.set(nearestStationDistance)

        #Atualiza texto de informacao da proxima compra a ser realizada
        if(len(nextPurchaseID) > 0):
            next_purchase_info_text.set(" UUID da compra: " + nextPurchaseID + " / TOTAL: " + nextAmountToPay + " ")
        else:
            next_purchase_info_text.set(" Não existe compra esperando confirmação. ")

        #Atualiza texto de informacao da ultima compra realizada
        next_purchase_result_text.set(purchaseResult)

        #Atualiza texto das informacoes do historico de compra
        purchaseHistoryID.set(" UUID da compra no histórico: " + displayPurchaseID + " ")
        purchaseHistoryTotal.set(" Valor Total da compra no histórico (BRL): " + displayPurchaseTotal + " ")
        purchaseHistoryPrice.set(" Preço do KWh da compra no histórico (BRL): " + displayPurchasePrice + " ")
        purchaseHistoryCharge.set(" Carga total da compra no histórico (KWh): " + displayPurchaseCharge + " ")


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
purchaseHistoryIndex = "0"
displayPurchaseID = "0"
displayPurchaseTotal = "0"
displayPurchasePrice = "0"
displayPurchaseCharge = "0"

#Cria um dicionario dos atributos do veiculo
dataTable = {}

#Pergunta endereco do servidor
serverAddress = input("Insira o endereço IP do servidor: ")

#Verifica se o arquivo de texto "ID.txt" esta presente, e caso nao esteja...
if (verifyFile(["vehicledata"], "ID.txt") == False):
    
    #Cria um novo arquivo
    writeFile(["vehicledata", "ID.txt"], vehicle.registerVehicle())

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
userID.pack(pady=20)

battery_info_text = ctk.StringVar()
battery_info = ctk.CTkLabel(frame,textvariable=battery_info_text)
battery_info.pack(pady=10)

critical_battery_text = ctk.StringVar()
critical_battery = ctk.CTkLabel(frame,textvariable=critical_battery_text)
critical_battery.pack(pady=20)

spotRequestButton = ctk.CTkButton(frame,text=' Obter a distância até a estação de recarga mais próxima e o preço do KWh ',command=lambda:vehicle.nearestSpotRequest())
spotRequestButton.pack(pady=10)

distance_info_text = ctk.StringVar()
distance_info = ctk.CTkLabel(frame,textvariable=distance_info_text)
distance_info.pack(pady=20)

simulatePayButton = ctk.CTkButton(frame,text=' Gerar guia de pagamento ',command=lambda:vehicle.simulateForNearestSpot())
simulatePayButton.pack(pady=10)

next_purchase_info_text = ctk.StringVar()
next_purchase_info = ctk.CTkLabel(frame,textvariable=next_purchase_info_text)
next_purchase_info.pack(pady=20)

bookButton = ctk.CTkButton(frame,text=' Recarregar totalmente na estação mais próxima ',command=lambda:vehicle.payForNearestSpot())
bookButton.pack(pady=10)

next_purchase_result_text = ctk.StringVar()
next_purchase_result = ctk.CTkLabel(frame,textvariable=next_purchase_result_text)
next_purchase_result.pack(pady=30)

purchaseHistoryID = ctk.StringVar()
purchaseHistoryIDLabel = ctk.CTkLabel(frame,textvariable=purchaseHistoryID)
purchaseHistoryIDLabel.pack(pady=5)

purchaseHistoryTotal = ctk.StringVar()
purchaseHistoryTotalLabel = ctk.CTkLabel(frame,textvariable=purchaseHistoryTotal)
purchaseHistoryTotalLabel.pack(pady=5)

purchaseHistoryPrice = ctk.StringVar()
purchaseHistoryPriceLabel = ctk.CTkLabel(frame,textvariable=purchaseHistoryPrice)
purchaseHistoryPriceLabel.pack(pady=5)

purchaseHistoryCharge = ctk.StringVar()
purchaseHistoryChargeLabel = ctk.CTkLabel(frame,textvariable=purchaseHistoryCharge)
purchaseHistoryChargeLabel.pack(pady=10)

bckButton = ctk.CTkButton(frame,text=' < ',command=lambda:vehicle.purchaseBackward())
bckButton.pack(pady=5)

bckButton = ctk.CTkButton(frame,text=' > ',command=lambda:vehicle.purchaseForward())
bckButton.pack(pady=20)

newThread = threading.Thread(target=infoUpdate, args=())
newThread.start()

frame.mainloop()