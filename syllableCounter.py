import string

class syllableCounter:
	
	syllableMap = dict()
	
	emphasisMap = dict()
	
	rhymeMap = dict()
	
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
					keyWord = cleaned.split()[0].translate(string.maketrans("",""), string.punctuation)
					keyWord = ''.join([i for i in keyWord if not i.isdigit()])
					self.emphasisMap[keyWord] = emphasis
					emphasisVowel = None
					cleaned = ' '.join(cleaned.split()[1::])
					cleaned = cleaned.strip()
					cleaned = cleaned.replace("2", "1")
					cleaned = cleaned.replace("0", "1")
					for word in cleaned.split():
						if word.find("1") != -1:
							emphasisVowel = word[:-1]
					if emphasisVowel != None:
						if emphasisVowel not in self.rhymeMap:
							self.rhymeMap[emphasisVowel] = list()
						self.rhymeMap[emphasisVowel].append(keyWord)
							
				
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
				words.append(word.lower())
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

	def doWordsRhyme(self, word1, word2):
		word1 = word1.upper()
		word2 = word2.upper()
		list1 = [k for k, v in self.rhymeMap.iteritems() if word1 in v]
		list2 = [k for k, v in self.rhymeMap.iteritems() if word2 in v]
		list3 = [val for val in list1 if val in list2]
		if len(list1) == 0 or len(list2) == 0:
			return False
		elif len(list3) == 0:
			return False
		return True