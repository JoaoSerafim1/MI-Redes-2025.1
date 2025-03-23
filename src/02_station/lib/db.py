import os
import json


#Funcao que verifica se existe um arquivo especifico no diretorio fornecido
def verifyFile(pathList, fileName):

    #String do caminho a ser aberto, inicialmente vazia
    pathString = ""

    #Percorre a lista do caminho de forma a construir a string deste
    for pathIndex in range(0, len(pathList)):
        
        pathString = os.path.join(pathString, pathList[pathIndex])

    if pathString != "":
        #Lista dos arquivos presentes no diretorio especificado
        try:
            fileList = os.listdir(pathString)
        except:
            return False
    else:
        fileList = os.listdir()

    #Verifica se existe o arquivo especificado
    if (fileName in fileList):

        return True
    
    return False


#Funcao que cria um arquivo baseando em uma lista com o caminho dele e um dicionario do conteudo a ser adicionado 
def createFile(pathList, contentTable):

    #String do caminho a ser aberto, inicialmente vazia
    pathString = ""

    #Percorre a lista do caminho de forma a construir a string deste
    for pathIndex in range(0, len(pathList)):
        
        pathString = os.path.join(pathString, pathList[pathIndex])

    #Abre o arquivo em modo de escrita
    with open(pathString, "w") as file:
        
        #Joga o conteudo do dicionario no arquivo por meio de json
        json.dump(contentTable, file)


#Funcao que le um arquivo baseado em uma lista com o caminho dele
def readFile(pathList):

    #String do caminho a ser aberto, inicialmente vazia
    pathString = ""

    #Percorre a lista do caminho de forma a construir a string deste
    for pathIndex in range(0, len(pathList)):
        
        pathString = os.path.join(pathString, pathList[pathIndex])
    
    #Abre o arquivo em modo de leitura
    with open(pathString, "r") as file:
        
        #Retorna o conteudo carregado por meio de json
        return json.load(file)
    

#Funcao que atualiza um arquivo baseado em uma lista com o caminho dele e um dicionario do conteudo a ser atualizado
def updateFile(pathList, newTable):

    #String do caminho a ser aberto, inicialmente vazia
    pathString = ""

    #Percorre a lista do caminho de forma a construir a string deste
    for pathIndex in range(0, len(pathList)):
        
        pathString = os.path.join(pathString, pathList[pathIndex])
    
    #Dicionario vazio
    contentTable = {}

    #Abre o arquivo em modo de leitura
    with open(pathString, "r") as file:
        
        #Carrega o conteudo do arquivo por meio de json
        contentTable = json.load(file)

    #Abre o arquivo em modo de escrita
    with open(pathString, "w") as file:

        #Percorre o dicionario do conteudo a ser atualizado
        for key in newTable:

            #Atualiza valores
            contentTable[key] = newTable[key]

        #Joga o conteudo do dicionario no arquivo por meio de json
        json.dump(contentTable, file)