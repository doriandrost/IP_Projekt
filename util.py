import hashlib

def DicToString(dic):
	res = ""
	for key in dic:
		res += key
		res += "$"
		res += dic[key]
		res += "|"
	print(res)
	return res[:-1] if res[-1] == "|" else res

def StringToDic(string):
	res = {}
	for entry in string.split("|"):
		key,val = entry.split("$")[0], entry.split("$")[1]
		res.update({key:val})
	return res

def Hash(string):
	#return hashlib.md5(bytes(string,"utf-8")).hexdigest()	#seems to be indeterministic
	fold = [1,3,6,2,7,9,4,2,7,9]
	exps = [2,3,2,4,3,1,1,2,3,1,4]
	s = 0
	for i,f in enumerate(string):
		s += (fold[i % len(fold)] * ord(f))**exps[i % len(exps)]
	return str(s)[:64]

def KryptoHash(string):
	fold = [1,3,6,2,7,9,4,2,7,9]
	exps = [2,3,2,4,3,1,1,2,3,1,4]
	s = 0
	for i,f in enumerate(string):
		s += (fold[i % len(fold)] * ord(f))**exps[i % len(exps)]
	return str(s)[:64]

def encrypt(text,password):
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

def decrypt(text,password):
	b = len(password)
	width = len(text) // b
	sortedpw = sorted(password)
	columns = list()
	for i in range(0,width*(len(text) // width),width):
		columns.append(text[i:i+width])
	columns = list(zip(sortedpw,columns))
	print(columns)
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
	print(reorderedcols)
	for i in range(width):
		l = "".join(list(map(lambda z : z[1][i],reorderedcols)))
		lines.append(l)
	lines = "".join(lines)
	while lines[-1] == "X":
		lines = lines[:-1]
	return lines





text = "SomeTextAndSomeMoreTextAndEvenMore"
password = "fisch"
c = encrypt(text,password)
print(c)
d = decrypt(c,password)
print(d)
