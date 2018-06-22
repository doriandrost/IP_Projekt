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