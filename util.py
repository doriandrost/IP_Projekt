import hashlib

def DicToString(dic):
	"""
	Converts a Dicitionary to a String.
	This is done throuhg seperating the entries and its values with seperators such as
	"$" and "|". 
	"""
	res = ""
	for key in dic:
		res += key
		res += "$"
		res += dic[key]
		res += "|"
	return res[:-1] if res[-1] == "|" else res

def StringToDic(string):
	"""
	Guess what: Converts a String to a Dictionary
	"""
	res = {}
	for entry in string.split("|"):
		key,val = entry.split("$")[0], entry.split("$")[1]
		res.update({key:val})
	return res

def Hash(string):
	"""
	Calculates a hash for a given string for the Prüfsumme.
	This hashfunction is just made up. One could implement any hash function at this place.
	"""
	fold = [1,3,6,2,7,9,4,2,7,9]
	exps = [2,3,2,4,3,1,1,2,3,1,4]
	s = 0
	for i,f in enumerate(string):
		s += (fold[i % len(fold)] * ord(f))**exps[i % len(exps)]
	return str(s)[:64]


def encrypt_once(text,password):
	"""
	encrypts the given text with the given password with a columntransposition

	"""
	b = len(password)
	while(len(text) % b != 0):	#padding
		text += "X"
	lines = list()
	for i in range(0,b*(len(text) // b),b):
		lines.append(text[i:i+b])
	columns = list()
	for i in range(len(password)):
		col = (password[i],list(map(lambda z : z[i],lines)))
		columns.append(col)
	orderedcols = sorted(columns,key = lambda z : z[0])
	ret = "".join(list(map(lambda z : "".join(z[1]),orderedcols)))
	return ret

def decrypt_once(text,password,cut = False):
	"""
	Decrypts the given ciphertext with the password using a columntransposition.
	The parametre cut defines, whether the padding Xs at the end should be cut off.
	If the return value of this is the encrypted string, one should cut them off.
	If however the value should be decrypted once more, one should not.
	"""
	b = len(password)
	width = len(text) // b
	sortedpw = sorted(password)
	columns = list()
	for i in range(0,width*(len(text) // width),width):
		columns.append(text[i:i+width])
	columns = list(zip(sortedpw,columns))
	reorderedcols = list()
	for letter in password:
		matchingcol = list()
		for col in columns:
			if col[0] == letter:
				matchingcol = col
				columns.remove(col)
				break
		reorderedcols.append(matchingcol)
	lines = list()
	for i in range(width):
		l = "".join(list(map(lambda z : z[1][i],reorderedcols)))
		lines.append(l)
	lines = "".join(lines)
	if(cut):
		while lines[-1] == "X":
			lines = lines[:-1]
	return lines


def encrypt(text,password):
	"""
	encrypts the given text with the password as a "Doppelwürfel"
	The "Doppelwürfel" is still undecryptable.
	"""
	#p1,p2 = password[:len(password)//2],password[len(password)//2:]
	#print(p1,p2)
	c = encrypt_once(text,password)
	cc = encrypt_once(c,password)
	return cc

def decrypt(text,password):
	"""
	decrypts the given ciphertext with the password as a "Doppelwürfel"
	"""
	#p1,p2 = password[:len(password)//2],password[len(password)//2:]
	#print(p1,p2)
	d = decrypt_once(text,password,cut = False)
	dd = decrypt_once(d,password,cut=True)
	return dd


#text = "ID$35774998974437|TYPE$1"
#print(text,len(text))
#print("......")
#a = encrypt(text,"schwammkopf")
#print(a,len(a))
#b = decrypt(a,"schwammkopf")
#print(b,len(b))