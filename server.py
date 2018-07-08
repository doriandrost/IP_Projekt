#!/usr/bin/env python3
import socket
import time
import util
from threading import Thread
import sys
from zipfile import ZipFile
import getpass

host = "localhost"
port = 5026
EOT = "EOT"

secure,password = sys.argv[1] == str(1),"fischkopf"

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
		self.TimerDeamon = None
		self.startTimerDeamon()
		self.startListeningThread()

		self.UpdateRules = {"One_Package":"42","Another_Package":"1.5"}

#		#self.Packages.append({"Name":"Ein Package", "URL":"www.google.com", "Version":"42"})

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
		#print("Server: Start listening...")
		self.s.listen(socket.SOMAXCONN)
		self.inSocket, self.addr = self.s.accept()
		#print("Server: accepted a connection")
		self.waitForIncom()

	def send(self,message):
		"""
		sends the message via the inSocket.
		"""
		#print("Server: Sending the message ",message)
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
			#print(b)
			#print(recievedBytes)
			#print(EOT in recievedBytes)
			if(len(b) == 0):
				break
			if(EOT in recievedBytes):
				recievedBytes = recievedBytes[:-len(EOT)]	#cut the EOT
				break
		#print("Server: Recieved a Message that is: \n",recievedBytes)
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
		TYPE 3 : signal to remove this client of the list
		"""
		if(secure):
			St = util.decrypt(St,password)
		try:
			incom = util.StringToDic(St)
		except:
			print("Something went wrong. The password may have been in correct")
			self.send("1")
			return
#		print(incom)
		if(incom["TYPE"] == "0"):#0 register
			if(incom["ID"] not in self.All_Clients):
				del incom["TYPE"]	#we don't want to store that information in the dic
				incom.update({"TIMESTAMP":time.time()})
				p = {}
				for k in self.UpdateRules:
					p.update({k:"0"})
				incom.update({"PACKAGE_VERSIONS":p})
				self.All_Clients.update({incom["ID"]:incom})
				print("Server: sucesfully registered a new Client with id",incom["ID"])
				self.send("0")
			else:
				self.send("1")
		elif(incom["TYPE"] == "1"): #1 heartbeat
			if(incom["ID"] in self.All_Clients):
				self.All_Clients[incom["ID"]].update({"TIMESTAMP":time.time()})
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
		elif(incom["TYPE"] == "3"): #3 deregister
			del self.All_Clients[incom["ID"]]
			self.send("0")
	def readInPackage(self, name):
		"""
		reads in the zipfile archive specified through the name.
		returns a dic of the form {"NAME":name,"TIMESTAMP":"42",bla:blub, spamm:eggs ...}
		where the keys are the names of the files and the values their content.
		"""
		#print("reading in packages...")
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
		for package in self.UpdateRules:
			if float(self.UpdateRules[package]) > float(self.All_Clients[clientDic["ID"]]["PACKAGE_VERSIONS"][package]):
				pack = self.readInPackage(str(package)+".zip")
				self.All_Clients[clientDic["ID"]]["PACKAGE_VERSIONS"][package] = self.UpdateRules[package]
				return pack
		return 1

	def startTimerDeamon(self):
		"""
		Starts a new thread that checks from time to time, whether the clients last heartbeat is not too old.
		If he identifies clients as outdates he removes them of the client list.
		"""
		self.TimerDeamon = Thread(target = self.timerDeamon)
		self.TimerDeamon.daemon = True	#so it stoppes correctly as the server shuts down
		self.TimerDeamon.start()

	def timerDeamon(self):
		while 1:
			time.sleep(30)
			print("waking up")
			tokill = list()
			for client in self.All_Clients:
				if (time.time() - self.All_Clients[client]["TIMESTAMP"] > 90):
					print(client, "killed by the TimeDeamon")
					tokill.append(client)
			for client in tokill:
				del self.All_Clients[client]

	def registerClient(self,identifier,client):
		self.All_Clients.update({identifier:client})

	def detachClient(self,identifier):
		self.All_Clients.pop(identifier)

	def getInfo(self,identifier):
		return self.All_Clients[identifier]

	def getAllClients(self):
		return list(self.All_Clients.keys())

		

Serv = Server()

if(secure):
	print("Bitte definieren Sie das Masterpassword des Servers:")
	j = getpass.getpass()
	password = j

while True:
	i = input(">")
	if(i == "allclients"):
		print (Serv.getAllClients())
	elif(i in Serv.All_Clients):
		print(Serv.getInfo(i))
	elif("remove" in i):
		tokill = i[len("remove "):]
		del Serv.All_Clients[tokill]
		print("removed client ",tokill)
	elif(i == "quit"):
		sys.exit()








