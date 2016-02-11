import string

class syllableCounter:
	
	syllableMap = dict()
	
	emphasisMap = dict()
	
	def __init__(self):
		with open("syllables_dict.txt") as f:
			for line in f:
				cleaned = line.rstrip('\n')
				self.syllableMap[cleaned.split(",")[0]]=int(cleaned.split(",")[1])
		with open("cmudict7b.txt") as f:
			for line in f:
				if not line.startswith(";;;"):
					cleaned = line.rstrip('\n')
					emphasisStr = ''.join(cleaned.split()[1::])
					emphasisStr = emphasisStr.replace("2", "1")
					emphasis = [int(s) for s in emphasisStr if s.isdigit()]
					self.emphasisMap[cleaned.split()[0].translate(string.maketrans("",""), string.punctuation)] = emphasis
				
	def getSyllablesOf(self, word):
		try:
			return self.syllableMap[word.lower()]
		except KeyError:
			print("Key error on "+word)
			return 0
			
	
	def getEmphasisOf(self, word):
		try:
			return self.emphasisMap[word.upper()]
		except KeyError:
			print("Key error on "+word)
			return 0
			
	def getWordsWithEmphasis(self, emphasis):
		words = []
		for word, wordEmphasis in self.emphasisMap.iteritems():
			if wordEmphasis == emphasis:
				words.append(word)
		return words
		
	def getWordsWithSyllableCount(self, syllableCount):
		words = []
		for word, wordSyllables in self.syllableMap.iteritems():
			if wordSyllables == syllableCount:
				words.append(word)
		return words
		
	def getAllWords(self):
		words = []
		for word, wordSyllables in self.syllableMap.iteritems():
			words.append(word)
		return words