#!/usr/bin/env python3
import socket
import time
import util
from threading import Thread
import sys
from zipfile import ZipFile


host = "localhost"
port = 5026
EOT = "EOT"

secure,password = True,"fisch"




class Server():


	def __init__(self):
		"""
		Initialises the class (guess what...).
		Sets its variables, among these are:
		All_Clients: a Dict containing all clients of the form {ID:Info} with Info = {GPU:XY,RAM:100...}
		Packages: A list of all Packages. Listentries are Dictionarys of the form {Name:Blub, URL:Bla, version:42...}
		"""
		#A Dic containing all clients Id -> Cl where Cl is a Dic itself containing
		#Hostname,Ip, etc
		self.All_Clients = {}
		self.Packages = list()
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
		self.s.bind((host,port))
		self.inSocket = None
		self.addr = None
		self.listeningThread = None

		self.Packages.append({"Name":"Ein Package", "URL":"www.google.com", "Version":"42"})

	def startListeningThread(self):
		"""
		Starts the thread that listens to clients. This is done in a seperate thread so the server can still
		interact with the user at the same time.
		"""
		self.listeningThread = Thread(target = self.listen)
		self.listeningThread.daemon = True	#so it stoppes correctly as the server shuts down
		self.listeningThread.start()

	def listen(self):
		"""
		Listens with s.listen until a connection is there.
		Calls waitForIncom, as soon as a connection is established.
		"""
		print("Server: Start listening...")
		self.s.listen(socket.SOMAXCONN)
		self.inSocket, self.addr = self.s.accept()
		print("Server: accepted a connection")
		self.waitForIncom()

	def send(self,message):
		"""
		sends the message via the inSocket.
		"""
		print("Server: Sending the message ",message)
		if(len(message) == 1):
			self.inSocket.send(bytes(message,"utf-8"))
		else:
			self.inSocket.send(bytes(message + EOT,"utf-8"))


	def waitForIncom(self):
		"""
		recieves data. All Data sent has to end with the EOT.
		Calls ExtractInfoFromString afterwards to handle the input.
		"""
		recievedBytes = ""
		while True:
			#time.sleep(1)
			#print("Server: Waiting for Incom...")
			b = self.inSocket.recv(10)
			recievedBytes += b.decode("utf-8")
			print(b)
			print(recievedBytes)
			print(EOT in recievedBytes)
			if(len(b) == 0):
				break
			if(EOT in recievedBytes):
				recievedBytes = recievedBytes[:-len(EOT)]	#cut the EOT
				break
		print("Server: Recieved a Message that is: \n",recievedBytes)
		self.ExtractInfoFromString(recievedBytes)
		self.startListeningThread()

	def ExtractInfoFromString(self,St):
		"""
		Handles the input St accordingly to its Type.
		Uses util.StringToDic to translate the String St to a Dictionary.
		The dictionary conaints the key TYPE that specifies, what the sent data wants to do:
		TYPE 0 : register
		TYPE 1 : heartbeat
		TYPE 2 : question for packages
		"""
		if(secure):
			St = util.decrypt(St,password)
		print("ST",St)
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
			if(incom["ID"] in self.All_Clients):
				self.All_Clients[incom["ID"]].update({"Timestamp":time.asctime()})
				self.send("0")
			else:
				self.send("1")
		elif(incom["TYPE"] == "2"): #2 anfrage
			updates = self.searchForUpdates(incom)
			if(updates != 1):
				self.send("0")
				self.send(updates)
			else:
				self.send("1")
	def readInPackage(self, name):
		"""
		reads in the zipfile archive specified through the name.
		returns a dic of the form {"NAME":name,"TIMESTAMP":"42",bla:blub, spamm:eggs ...}
		where the keys are the names of the files and the values their content.
		"""
		print("reading in packages...")
		packages_dic = {}
		package = ZipFile(name,"r")
		for member in package.namelist():
			packages_dic.update({member:package.open(member,"r").read().decode("utf-8")})
		packages_dic.update({"TIMESTAMP":str(time.time())})
		packages_dic.update({"NAME":name})
		packages_dic.update({"CHECKSUM":str(util.Hash(util.DicToString(packages_dic)))})
		ret = util.DicToString(packages_dic)
		if(secure):
			ret = util.encrypt(ret,password)
		return ret

	def searchForUpdates(self, clientDic):
		"""
		searches for whether there are packageupdates available for the client specified in clientDic. 
		"""
		pack = self.readInPackage("One_Package.zip")
		return pack

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








