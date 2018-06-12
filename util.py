

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
