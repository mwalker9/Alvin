import os
import string
from stop_words import get_stop_words
import syllableCounter

class Alvin:
	
	def __init__(self):
		self.inspirationSet = []
		self.stopWords = get_stop_words('en')
	
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
		return
	
	def transformTheme(self, data):
		return
	
	def getRhymeScheme(self, data):
		return
	
	def getMeter(self, data):
		ctr = syllableCounter.syllableCounter()
		a = []
		for word in data.split(" "):
			a = a + ctr.getEmphasisOf(word)
		return a
	
	def isWordImportant(self, data):
		if data in self.stopWords:
			return True
		else:
			return False
	
	def getNewLine(self, editedLine, transformedText, rhymeScheme, meter, newTheme, oldTheme): #magic happens
		return
	
	def run(self):
		self.LoadInspirationSet()
		data = self.LoadOriginal()
		theme = self.getTheme(data)
		newTheme = self.transformTheme(data)
		rhymeScheme = self.getRhymeScheme(data)
		transformedText = []
		for line in data:
			meter = self.getMeter(data)
			editedLine = ""
			for word in line.split(" "):
				if self.isWordImportant(word):
					editedLine = editedLine.join(" ".join(word))
				else:
					editedLine = editedLine.join(" ".join("_"))
			transformedText.append(self.getNewLine(editedLine, transformedText, rhymeScheme, meter, newTheme, theme))
		
		for line in transformedText:
			print(line)
				
				
			
		
