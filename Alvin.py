import os
import string

class Alvin:
	
	def __init__(self):
		self.inspirationSet = []
	
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
		return
	
	def getTheme(self, data):
		return
	
	def transformTheme(self, data):
		return
	
	def getRhymeScheme(self, data):
		return
	
	def getMeter(self, data):
		return
	
	def isWordImportant(self, data):
		return
	
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
				
				
			
		