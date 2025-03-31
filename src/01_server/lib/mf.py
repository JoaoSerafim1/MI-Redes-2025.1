import math

#Funcao para calcular distancia entre dois pontos
#Versao de teste (linear), pode ser substituida por uma versao que calcula o comprimento do arco sobre a superficie da terra com base em um conjunto de duas coordenadas de GPS distintas
def getDistance(x1, y1, x2, y2):

    dx = abs(x2-x1)
    dy = abs(y2-y1)

    return math.sqrt((dx^2)+(dy^2))