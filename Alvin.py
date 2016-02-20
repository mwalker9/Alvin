import random
import os
import string
from stop_words import get_stop_words
import syllableCounter
import word2vec
import nltk
from RhymeDictionary import RhymeDictionary

class Alvin:
	
	def __init__(self):
		os.environ['STANFORD_PARSER'] = './stanford-postagger-full-2014-08-27'
		os.environ['CLASSPATH'] = './stanford-postagger-full-2014-08-27'
		os.environ['STANFORD_MODELS'] = './stanford-postagger-full-2014-08-27'
		self.pos = nltk.tag.stanford.StanfordPOSTagger('models/english-bidirectional-distsim.tagger')
		self.inspirationSet = []
		self.stopWords = get_stop_words('en')
		self.model = word2vec.load('./wikipedia_articles.bin')
		self.ctr = syllableCounter.syllableCounter()
		self.rhymeDictionary = RhymeDictionary()
		self.rhymeDictionary.loadRhymeFiles()
	
	def LoadInspirationSet(self):
		inspirationDirectory = "./InspirationSet/"
		for file in os.listdir(inspirationDirectory):
			with open(inspirationDirectory+file) as f:
				for line in f:
					out = line.translate(string.maketrans("",""), string.punctuation)
					out = out.strip()
					for word in out.split(" "):
						if word:
							self.inspirationSet.append(word)
		
		
	def LoadOriginal(self):
		inspirationFile = "./original.txt"
		finalData = []
		with open(inspirationFile) as f:
			for line in f:
				out = line.translate(string.maketrans("",""), string.punctuation)
				out = out.strip()
				finalData.append(out)
		return finalData
				
	def getTheme(self, data):
		temp = [data[i].split() for i in range(len(data))]
		temp = [temp[i][j] for i in range(len(temp)) for j in range(len(temp[i]))]
		temp2 = []
		for word in temp:
			if self.isWordImportant(word) and word in self.model.vocab:
				temp2.append(word)
		indexes, sim = self.model.analogy(pos=temp2, neg=[])
		theme = self.model.vocab[indexes[0]]
		print(theme)
		return theme
	
	def transformTheme(self, theme):
		indexes, sim = self.model.analogy(pos=[], neg=[theme])
		theme = self.model.vocab[indexes[0]]
		print(theme)
		return theme
	
	def getRhymeScheme(self, data):
		return
	
	def getMeter(self, data):
		a = []
		for word in data.split(" "):
			a.append(self.ctr.getEmphasisOf(word))
		return a
	
	def isWordImportant(self, data):
		if data in self.stopWords:
			return False
		else:
			return True
	
	def getNewLine(self, PoS, editedLine, transformedText, rhymeScheme, meter, newTheme, oldTheme): #magic happens
		newLine = ""
		allwords = self.ctr.getAllWords()
		originalPoS = [PoS[i][1] for i in range(len(PoS))]
		newLine = ""
		i = 0
		for word in editedLine.split():
			newWord = ""
			if word == "_":
				#while len(self.getPartOfSpeechTags(newWord)) != 1 or self.getPartOfSpeechTags(newWord)[0][1] != originalPoS[i]:
				newWord = allwords[random.randint(0, len(allwords))]
				newLine = newLine + " " + newWord
			else:
				newLine = newLine + " " + word
			i = i + 1
		return newLine.strip()
	
	def getPartOfSpeechTags(self, line):
		return self.pos.tag(line.split())
	
	def run(self):
		self.LoadInspirationSet()
		data = self.LoadOriginal()
		theme = self.getTheme(data)
		newTheme = self.transformTheme(theme)
		rhymeScheme = self.getRhymeScheme(data)
		transformedText = []
		for line in data:
			wordNumber = 0
			PoS = self.getPartOfSpeechTags(line)
			meter = self.getMeter(line)
			editedLine = ""
			for word in line.split():
				if not self.isWordImportant(word):
					editedLine = editedLine + " " + word
				else:
					editedLine = editedLine + " _"
				wordNumber = wordNumber + 1
			#print(editedLine)
			transformedText.append(self.getNewLine(PoS, editedLine.strip(), transformedText, rhymeScheme, meter, newTheme, theme))
		print("DONE!")
		print("")
		
		for line in transformedText:
			print(line)

if __name__ == '__main__':
		print "Loading Alvin..."
		a = Alvin()
		print "Running..."
		a.run()
