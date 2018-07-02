#!/usr/bin/env python3
import socket
import util
import sys
import platform
import uuid
import os
import re
import getpass

secure,password = True,"fischkopf"

host = "localhost"
port = 5019
EOT = "EOT"

identifier = sys.argv[1] if len(sys.argv) > 1 else uuid.getnode()

class Client():

	def __init__(self,identifier,host,port):
		self.identifier = identifier
		self.host,self.port = host,port
	
	def register(self):
		"""
		registers itself to the server.
		returns a "0" if everything was sucesfull, a "1" otherwise
		"""
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
		s.connect((host,port))
		cpu, system, version = platform.processor(), platform.system(), platform.version()
		machine = platform.machine()
		if(identifier != 0):
			mac = identifier
		else:
			mac = str(uuid.getnode())
		myInfo = {"TYPE":"0","ID":str(mac),"CPU":cpu,"SYSTEM":system,"VERSION":version}
		infoString = util.DicToString(myInfo)
		if(secure):
			infoString = util.encrypt(infoString,password)
		#print("Client: Sending my info: ",infoString)
		s.send(bytes(infoString,"utf-8"))
		#print("Sending", EOT)
		s.send(bytes(EOT,"utf-8"))
		answer = s.recv(1).decode("utf-8")
		#print("Server answered with", answer)
		#if(answer == "1"):
		#	print("poor :(")
		#elif(answer == "0"):
		#	print("yeah :)")

		#print("answer",answer)
		s.close()
		return answer

	def heartbeat(self):
		"""
		sends a heartbeat to the server.
		Returns a "0" if sucesfull, a "1" otherwise
		"""
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
		s.connect((host,port))
		heartbeat = {"TYPE":"1","ID":str(identifier)}
		#print(heartbeat)
		heartbeatString = util.DicToString(heartbeat)
		if(secure):
			heartbeatString = util.encrypt(heartbeatString,password)
		#print("Sending a message that is", heartbeatString)
		s.send(bytes(heartbeatString,"utf-8"))
		#print("Sending", EOT)
		s.send(bytes(EOT,"utf-8"))
		answer = s.recv(1).decode("utf-8")
		s.close()

		return answer

	def suicide(self):
		"""
		deregisters the client from the server.
		recieves an answer "0" if sucesfull, "1" otherwise.
		"""
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
		s.connect((host,port))
		query = {"ID":identifier,"TYPE":"3"}
		queryAsString = util.DicToString(query)
		if(secure):
			queryAsString = util.encrypt(queryAsString,password)
		s.send(bytes(queryAsString,"utf-8"))
		#print("sending",queryAsString)
		s.send(bytes(EOT,"utf-8"))
		answer = s.recv(1).decode("utf-8")
		return answer

	def ask(self):
		"""
		Asks the server if there are packageupdates available.
		Receives the packages and calls the InstallPackages function.
		Returns "0" if sucesfull, "1" otherwise.
		"""
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
		s.connect((host,port))
		question = {"ID":identifier,"TYPE":"2"}
		questionAsString = util.DicToString(question)
		if(secure):
			questionAsString = util.encrypt(questionAsString,password)
		#print("sending ",questionAsString)
		s.send(bytes(questionAsString,"utf-8"))
		#print("sending ",EOT)
		s.send(bytes(EOT,"utf-8"))
		answer = s.recv(1).decode("utf-8")
		#print(answer)
		if(answer == "0"):
			inp = ""
			while 1:
				inp += s.recv(10).decode("utf-8")
				if(EOT in inp):
					break
			d = inp[:-len(EOT)]
			if(secure):
				d = util.decrypt(d,password)
			self.installPackages(d)
		s.close()
		return answer

	def installPackages(self,pack_string):
		"""	
		Installs (i.e. creates the files of) the packages coming from the dict packages.
		"""
		packages = util.StringToDic(pack_string)
		checksum = packages["CHECKSUM"]
		del packages["CHECKSUM"]
		e = re.compile(r"(\|CHECKSUM\$)[0-9]*")
		q = e.search(pack_string)
		pack_string = pack_string[:q.start()] + pack_string[q.end():]
		calculated_checksum = util.Hash(pack_string)
		#print("calculated on:",pack_string)
		if(calculated_checksum != checksum):
			print("Checksums don't match!")
			print(checksum)
			print(calculated_checksum)
			return
		timestamp = packages["TIMESTAMP"]
		del packages["TIMESTAMP"]
		name = packages["NAME"][:-4]
		del packages["NAME"]
		print(name)
		os.mkdir(name)
		os.chdir(name)
		for name in packages:
			pack = open(name,"w")
			pack.write(packages[name])
			pack.close()
		os.chdir("..")

client = Client(identifier,host,port)
print("Client gestartet.")
print("Bitte geben Sie das Passwort für die Kommunikation zum Server ein")
j = getpass.getpass()
password = j
while True:
	i = input(">")
	if(i == "register"):
		print("registered. answer: ",client.register())
	elif(i == "heartbeat"):
		print("heartbeat. answer: ",client.heartbeat())
	elif(i == "ask"):
		print("asking. answer: ",client.ask())
	elif(i == "suicide"):
		print("commiting suicide. Answer:", client.suicide())
	elif(i == "quit"):
		sys.exit()
	


