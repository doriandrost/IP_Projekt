#!/usr/bin/env python3
import socket
import util

host = "localhost"
port = 5000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)

s.connect((host,port))

myInfo = {"TYPE":"0","ID":"1234","CPU":"SomeCPU","GPU":"SomeGPU","RAM":"1000"}
infoString = util.DicToString(myInfo)
print("Client: Sending my info: ",infoString)
s.send(bytes(infoString,"utf-8"))


s.close()