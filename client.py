#!/usr/bin/env python3
import socket
import util
import sys

host = "localhost"
port = 5018

identifier = sys.argv[1]

class Client():

	def __init__(self,identifier,host,port):
		self.identifier = identifier
		self.host,self.port = host,port
	
	def register(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
		s.connect((host,port))
		myInfo = {"TYPE":"0","ID":identifier,"CPU":"SomeCPU","GPU":"SomeGPU","RAM":"1000"}
		infoString = util.DicToString(myInfo)
		print("Client: Sending my info: ",infoString)
		s.send(bytes(infoString,"utf-8"))
		#s.close()
		#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
		#s.connect((host,port))
		answer = ""
		while True:
			inp = s.recv(1)
			answer += inp.decode("utf-8")
			if(len(inp) == 0):
				break
		print("answer",answer)
		s.close()
		return answer

	def heartbeat(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
		s.connect((host,port))
		heartbeat = {"TYPE":"1","ID":identifier}
		heartbeatString = util.DicToString(heartbeat)
		s.send(bytes(heartbeatString,"utf-8"))
		s.close()
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
		s.connect((host,port))
		answer = s.recv(1).decode("utf-8")
		s.close()

		return answer

	def ask(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
		s.connect((host,port))
		question = {"ID":identifier,"TYPE":"2"}
		questionAsString = util.DicToString(question)
		s.send(bytes(questionAsString,"utf-8"))
		s.close()
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
		s.connect((host,port))
		answer = s.recv(1).decode("utf-8")
		s.close()
		return answer

client = Client(identifier,host,port)
while True:
	i = input(">")
	if(i == "register"):
		print(client.register())
	elif(i == "heartbeat"):
		print(client.heartbeat())
	elif(i == "ask"):
		print(client.ask())
	elif(i == "quit"):
		sys.exit()
	


