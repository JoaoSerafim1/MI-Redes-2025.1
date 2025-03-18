import string
import random
import os
import json

lettersanddigits = string.ascii_uppercase + string.digits

randomID = ""

startInfo = {}
startInfo["name"] = "nobody"
startInfo["age"] = "23"

for count in range(0,24):
    randomID += random.choice(lettersanddigits)


filePath = (os.path.join("temp", (randomID + ".json")))

fileA = open(filePath, "w")
json.dump(startInfo, fileA)
fileA.close()

startInfo["name"] = "somebody"
startInfo["age"] = "41"

fileB = open(filePath, "r")
finalInfo = json.load(fileB)
fileB.close()

print(startInfo["name"])
print(startInfo["age"])
print(finalInfo["name"])
print(finalInfo["age"])