import socket

class User():
    def __init__(self,user,vehicle,payment_method,host): 
        self.user = user
        self.vehicle = vehicle
        self.battery_level = 1.0
        self.payment_method = payment_method
        self.payment_history = {}
        
        self.socket_sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        hostname = socket.gethostbyname(host)
        self.socket_sender.connect((hostname,8001))
        
    def batteryCheck(self): #notifica se a bateria esta em estado critico
        if self.battery_level < 0.3:
            return 1
        return 0
    
    def sendRequest(self): #envia requisicao simples (para fins de teste)
        self.socket_sender.sendall((str.encode('ok')))   
    
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