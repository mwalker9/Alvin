class syllableCounter:
	
	syllableMap = dict()
	
	def __init__(self):
		with open("syllables_dict.txt") as f:
			for line in f:
				cleaned = line.rstrip('\n')
				self.syllableMap[cleaned.split(",")[0]]=int(cleaned.split(",")[1])
				
	def getSyllablesOf(self, word):
		try:
			return self.syllableMap[word.lower()]
		except:
			print("Key error on "+word)
			return 0
			
	