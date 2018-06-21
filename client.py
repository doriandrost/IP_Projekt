#!/usr/bin/env python3
import socket
import util
import sys


host = "localhost"
port = 5025
EOT = "EOT"

identifier = sys.argv[1]

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
		myInfo = {"TYPE":"0","ID":identifier,"CPU":"SomeCPU","GPU":"SomeGPU","RAM":"1000"}
		infoString = util.DicToString(myInfo)
		print("Client: Sending my info: ",infoString)
		s.send(bytes(infoString,"utf-8"))
		print("Sending", EOT)
		s.send(bytes(EOT,"utf-8"))
		answer = s.recv(1).decode("utf-8")
		print("Server answered with", answer)
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
		heartbeat = {"TYPE":"1","ID":identifier}
		heartbeatString = util.DicToString(heartbeat)
		print("Sending a message that is", heartbeatString)
		s.send(bytes(heartbeatString,"utf-8"))
		print("Sending", EOT)
		s.send(bytes(EOT,"utf-8"))
		answer = s.recv(1).decode("utf-8")
		s.close()

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
		print("sending ",questionAsString)
		s.send(bytes(questionAsString,"utf-8"))
		print("sending ",EOT)
		s.send(bytes(EOT,"utf-8"))
		answer = s.recv(1).decode("utf-8")
		print(answer)
		if(answer == "0"):
			inp = ""
			while 1:
				inp += s.recv(10).decode("utf-8")
				if(EOT in inp):
					break
			d = util.StringToDic(inp[:-len(EOT)])
			print(d)
			self.installPackages(d)
		s.close()
		return answer

	def installPackages(self,packages):
		"""	
		Installs (i.e. creates the files of) the packages coming from the dict packages.
		"""
		timestamp = packages["TIMESTAMP"]
		del packages["TIMESTAMP"]
		for name in packages:
			pack = open(name,"w")
			pack.write(packages[name])
			pack.close()

client = Client(identifier,host,port)
while True:
	i = input(">")
	if(i == "register"):
		print("registered. answer: ",client.register())
	elif(i == "heartbeat"):
		print("heartbeat. answer: ",client.heartbeat())
	elif(i == "ask"):
		print("asking. answer: ",client.ask())
	elif(i == "quit"):
		sys.exit()
	


