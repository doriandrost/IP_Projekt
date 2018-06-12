#!/usr/bin/env python3
import socket
import time
import util
from threading import Thread
import sys


host = "localhost"
port = 5018




class Server():


	def __init__(self):
		#A Dic containing all clients Id -> Cl where Cl is a Dic itself containing
		#Hostname,Ip, etc
		self.All_Clients = {}
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
		self.s.bind((host,port))
		self.inSocket = None
		self.addr = None
		self.listeningThread = None

	def startListeningThread(self):
		self.listeningThread = Thread(target = self.listen)
		self.listeningThread.daemon = True	#so it stoppes correctly as the server shuts down
		self.listeningThread.start()

	def listen(self):
		print("Server: Start listening...")
		self.s.listen(socket.SOMAXCONN)
		self.inSocket, self.addr = self.s.accept()
		print("Server: accepted a connection")
		self.waitForIncom()

	def send(self,message):
		print("Server: Sending the message ",message)
		time.sleep(2)
		self.inSocket.send(bytes(message,"utf-8"))


	def waitForIncom(self):
		recievedBytes = ""
		while True:
			#time.sleep(1)
			#print("Server: Waiting for Incom...")
			b = self.inSocket.recv(10)
			recievedBytes += b.decode("utf-8")
			if(len(b) == 0):
				break
		print("Server: Recieved a Message that is: \n",recievedBytes)
		self.ExtractInfoFromString(recievedBytes)
		self.startListeningThread()

	def ExtractInfoFromString(self,St):
		incom = util.StringToDic(St)
		if(incom["TYPE"] == "0"):#0 register
			if(incom["ID"] not in self.All_Clients):
				del incom["TYPE"]	#we don't want to store that information in the dic
				incom.update({"Timestamp":time.asctime()})
				self.All_Clients.update({incom["ID"]:incom})
				print("Server: sucesfully registered a new Client")
				self.send("0")
			else:
				self.send("1")
		elif(incom["TYPE"] == "1"): #1 heartbeat
			self.All_Clients[incom["ID"]].update({"Timestamp":time.asctime()})
			self.send("0")
		elif(incom["TYPE"] == "2"): #2 anfrage
			pass
			self.send("0")



	def registerClient(self,identifier,client):
		self.All_Clients.update({identifier:client})

	def detachClient(self,identifier):
		self.All_Clients.pop(identifier)

	def getInfo(self,identifier):
		return self.All_Clients[identifier]

	def getAllClients(self):
		return list(self.All_Clients.keys())

		

Serv = Server()
Serv.startListeningThread()


while True:
	i = input(">")
	if(i == "allclients"):
		print (Serv.getAllClients())
	elif(i in Serv.All_Clients):
		print(Serv.getInfo(i))
	elif(i == "quit"):
		sys.exit()








