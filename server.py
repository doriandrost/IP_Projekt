



class Server():
	#A Dic containing all clients Id -> Cl where Cl is a Dic itself containing
	#Hostname,Ip, etc.
	All_Clients = {}


	def registerClient(self,identifier,client):
		self.All_Clients.update({identifier:client})

	def detachClient(self,identifier):
		self.All_Clients.pop(identifier)

	def getInfo(self,identifier):
		return self.All_Clients[identifier]

	def getAllClients(self):
		return self.All_Clients.keys()
