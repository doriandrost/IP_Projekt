#!/usr/bin/env python3
import socket
import time
import util


host = "localhost"
port = 5000
"""
try:
	while True:
		inSocket, addr = s.accept()
		inSocket.send(bytes("BLUB","utf-8"))
finally:
	inSocket.close()
"""



class Server():


	def __init__(self):
		#A Dic containing all clients Id -> Cl where Cl is a Dic itself containing
		#Hostname,Ip, etc
		self.All_Clients = {}
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
		self.s.bind((host,port))
		self.inSocket = None
		self.addr = None

	def listen(self):
		print("Server: Start listening...")
		self.s.listen(socket.SOMAXCONN)
		self.inSocket, self.addr = self.s.accept()
		print("Server: accepted a connection")

	def send(self,message):
		print("Server: Sending the message ",message)
		time.sleep(2)
		self.inSocket.send(bytes(message,"utf-8"))

	def waitForIncom(self):
		recievedBytes = ""
		while True:
			time.sleep(1)
			print("Server: Waiting for Incom...")
			b = self.inSocket.recv(10)
			recievedBytes += b.decode("utf-8")
			if(len(b) == 0):
				break
		print("Server: Recieved a Message that is: \n",recievedBytes)
		self.ExtractInfoFromString(recievedBytes)

	def ExtractInfoFromString(self,St):
		incom = util.StringToDic(St)
		if(incom["TYPE"] == "0"):#0 heartbeat
			del incom["TYPE"]	#we don't want to store that information in the dic
			self.All_Clients.update({incom["ID"]:incom})
		print("Server: sucesfully registered a new Client")




	def registerClient(self,identifier,client):
		self.All_Clients.update({identifier:client})

	def detachClient(self,identifier):
		self.All_Clients.pop(identifier)

	def getInfo(self,identifier):
		return self.All_Clients[identifier]

	def getAllClients(self):
		return list(self.All_Clients.keys())

Serv = Server()
Serv.listen()
Serv.waitForIncom()
print(Serv.getAllClients())
print(Serv.All_Clients)
