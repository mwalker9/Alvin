'''
popularity limits:
Only 350 words above 1,000,000
480 above 750,000
715 above 500,000
1427 above 250,000
1797 above 200,000
2023 above 175,000
2730 above 125,000
'''
import random
import os
import string
from stop_words import get_stop_words
import syllableCounter
import word2vec
import nltk
import numpy as np
from RhymeDictionary import RhymeDictionary
from robotbrain import RobotBrain
from nameList import nameList
import pickle
import Evaluate
import NGrams

class Alvin:
	
	def __init__(self):
		os.environ['STANFORD_PARSER'] = './stanford-postagger-full-2014-08-27'
		os.environ['CLASSPATH'] = './stanford-postagger-full-2014-08-27'
		os.environ['STANFORD_MODELS'] = './stanford-postagger-full-2014-08-27'
		self.pos = nltk.tag.stanford.StanfordPOSTagger('models/english-bidirectional-distsim.tagger')
		self.inspirationSet = []
		self.stopWords = get_stop_words('en')
		self.ctr = syllableCounter.syllableCounter()
		self.rhymeDictionary = RhymeDictionary()
		self.rhymeDictionary.loadRhymeFiles()
		self.robotBrain = RobotBrain()
		self.nameList = nameList()
		self.eval = Evaluate.Evaluator()
	
	def get_cosine_similarity(self, word1, word2):
		try:
			return self.robotBrain.get_cosine_similarity(word1, word2)
		except KeyError:
			return -1
	
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
			if self.isWordImportant(word) and word in self.robotBrain.model.vocab:
				temp2.append(word)
		indexes, sim = self.robotBrain.model.analogy(pos=temp2, neg=[])
		theme = self.robotBrain.model.vocab[indexes[random.randint(0,9)]]
		print(theme)
		return theme
	
	def transformTheme(self, theme):
		numberOfThemes = 1
		allwords = self.ctr.getAllWords()
		themes = []
		while(len(themes) < numberOfThemes):
			try:
				#perhaps make this a little more robust so we don't just keep getting errors forever
				indexes, sim = self.robotBrain.model.analogy(pos=[allwords[random.randint(0, len(allwords)-1)]], neg=[theme])
				for word in self.robotBrain.model.vocab[indexes]:
					if self.isWordImportant(word) and self.robotBrain.get_popularity(word) > 125000:
						themes.append(word)
						break
			except KeyError:
				print("FINE: Error on theme")
		return themes
	
	def getRhymeScheme(self, data):
		lastWords = [line.split()[len(line.split()) - 1] for line in data]
		rhymeScheme = [i for i in range(len(lastWords))]
		for i in range(len(lastWords)):
			if rhymeScheme[i] == i:
				for j in range(i+1, len(lastWords)):
					if self.ctr.doWordsRhyme(lastWords[i], lastWords[j]):
						rhymeScheme[j] = i
		return rhymeScheme
	
	def getMeter(self, data):
		a = []
		for word in data.split():
			a.append(self.ctr.getEmphasisOf(word))
		return a
	
	def isWordImportant(self, data):
		if data in self.stopWords:
			return False
		else:
			return True
	
	def evaluateLine(self, line):
		print "Evaluating", line
		words = line.split(' ')
		currentOrder = 1
		index = 0
		while (index + currentOrder) < len(words):				
			phrase = ""
			for i in xrange(index, currentOrder + index):
				phrase = phrase + " " + words[i]
			phrase = phrase.strip()
			possibleWord = words[i+1]
			#print phrase, possibleWord, currentOrder+1
			nGramMap = NGrams.getProbabilities(phrase, [possibleWord], currentOrder+1) #returns an array of maps -- need to convert
			nGramProbability = nGramMap[0]["probability"]
			#print phrase, possibleWord, nGramProbability
			if nGramProbability < -3.75:
				return False
			if currentOrder == 4:
				index += 1
			if currentOrder < 4:
				currentOrder += 1
		return True
			
	def Evaluate(self, transformedText, rhymeScheme):
		
		# first score each line according to how it conformed to its ryhme scheme
		linesThatRhymed = 0
		
		s = set(rhymeScheme)
		print 1.0 * len(s) / len(transformedText)
		
		for i, line in enumerate(transformedText):
			text = line.split(' ')
			# find the original line that this line needs to ryhme with
			seed = rhymeScheme[i]			
			
			# this is the word we are testing to see if it ryhmes with the seed line
			wordThatShouldRhyme = text[-1]
			
			# seed word
			seedWord = transformedText[seed].split(' ')[-1]
			
			# if the word is the seed line, we count it as a rhymed line and move on to the next word
			if i == seed:
				linesThatRhymed += 1
				continue
				
			# we will also allow the words to be the same
			if wordThatShouldRhyme == seedWord:
				linesThatRhymed += 1
				continue
			
			# get the set of ryhmed words that ryhme with the original line
			# eg
			# 0 hi you
			# 1 hello world
			# if seed == 0, then rhymedWords = ['true', 'blue', ...]
			rhymedWords = []
			try:
				rhymedWords = self.rhymeDictionary.getRhymes(seedWord)
			except:
				# the seed word was not found in the rhyme dictionary
				continue
			if wordThatShouldRhyme in rhymedWords:
				linesThatRhymed += 1
	
	def getNewLine(self, PoS, editedLine, transformedText, rhymeScheme, meter, newTheme, oldTheme, currentLineNumber): #magic happens
		newLine = ""
		allwords = self.ctr.getAllWords()
		originalPoS = ["_"+PoS[i][1] for i in range(len(PoS))]
		newLine = ""
		i = 0
		for word, part in zip(editedLine.split(), originalPoS):
			newWord = ""
			if word == "_":
				if part == "_NNP":
					part = "_NN"
				elif part == "_NNPS":
					part = "_NNS"
				allwords = self.ctr.getWordsWithEmphasis(meter[i])
				tempWords = [word for word in allwords if self.robotBrain.get_popularity(word) > 175000 and word not in self.nameList.names and self.robotBrain.get_most_likely_POS_tag(word) == part]
				if len(tempWords) != 0:
					allwords = tempWords
				else:
					print("failed", meter[i], part)
					newLine = newLine + allwords[random.randint(0, len(allwords)-1)]
					i = i + 1
					continue
				# if we are at the last word and the current line is not the first rhyming line in the series. ie [0,0,2,2] index != 1 || index != 3
				if i == len(editedLine.split())-1 and rhymeScheme[currentLineNumber] != currentLineNumber:
					# we retrieve the first line in the current ryhme series. ie [['hi', 'guys'],['burgers', 'fries'], ['spies', 'lies']], we would retrieve ['hi', 'guys']
					transformedLineBefore = transformedText[rhymeScheme[currentLineNumber]]
					# retrieve the last word from transformedLineBefore
					wordToRhyme = transformedLineBefore.split()[len(transformedLineBefore.split())-1]
					# retrieve all the rhyming words
					rhymes = self.rhymeDictionary.getRhymes(wordToRhyme)
					rhymes.append(wordToRhyme)
					if len(set(allwords) & set(rhymes)) > 0:
						# combine the rhyming words with the words that have the proper meter
						rhymes = list(set(allwords) & set(rhymes))
					# randomly select a word from this concatenated list; may not necessarily rhyme
					similarity = []
					for word in rhymes:
						similarity.append(self.get_cosine_similarity(word, newTheme))
					similarity = np.asarray(similarity)
					if similarity.min() < 0:
						similarity = similarity - similarity.min()
					if sum(similarity) == 0:
						similarity = np.ones(similarity.shape)
					similarity = similarity / sum(similarity)
					if newLine != "" or currentLineNumber == 0:
						probabilities = NGrams.getNGramProbabilities(newLine, rhymes)
					else:
						probabilities = NGrams.getNGramProbabilities(transformedText[currentLineNumber-1], rhymes)
					similarity = (similarity + 4 * probabilities) / 5.
					index = np.argmax(np.random.multinomial(1, similarity))
					while similarity[index] < 1./len(similarity):
						index = np.argmax(np.random.multinomial(1, similarity))
					newWord = rhymes[index]
				elif i == len(editedLine.split()) - 1:
					newWord = ""
					possibleWords = [w for w in allwords if self.rhymeDictionary.wordList.has_key(w)]
					probabilities = np.asarray(NGrams.getNGramProbabilities(newLine, possibleWords))
					index = np.argmax(np.random.multinomial(1, probabilities))
					while probabilities[index] < 1./len(probabilities):
						index = np.argmax(np.random.multinomial(1, probabilities))
					newWord = possibleWords[index]
				else:
					similarity = []
					for word in allwords:
						similarity.append(self.get_cosine_similarity(word, newTheme))
					similarity = np.asarray(similarity)
					if similarity.min() < 0:
						similarity = similarity - similarity.min()
					if sum(similarity) == 0:
						similarity = np.ones(similarity.shape)
					similarity = similarity / sum(similarity)
					if newLine != "" or currentLineNumber == 0:
						probabilities = NGrams.getNGramProbabilities(newLine, allwords)
					else:
						probabilities = NGrams.getNGramProbabilities(transformedText[currentLineNumber-1], allwords)
					similarity = (similarity + 4 * probabilities) / 5.
					index = np.argmax(np.random.multinomial(1, similarity))
					while similarity[index] < 1./len(similarity):
						index = np.argmax(np.random.multinomial(1, similarity))
					newWord = allwords[index]
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
		for currentTheme in newTheme:
			transformedText = []
			for line, lineNumber in zip(data, range(len(data))):
				wordNumber = 0
				PoS = self.getPartOfSpeechTags(line)
				meter = self.getMeter(line)
				editedLine = ""
				for word in line.split():
					# if a stop word and not the last word of the line or is the last word of a line and is the seed rhyme word
					if False and not self.isWordImportant(word) and (wordNumber != len(line.split()) - 1 or rhymeScheme[lineNumber] == lineNumber):
						# we add the stop word or a word in the case that it is the last word of the line
						editedLine = editedLine + " " + word
					else:
						# mark the space as needing to be replaced in the future
						editedLine = editedLine + " _"
					wordNumber = wordNumber + 1
				evaluation = False
				iteration = 0
				while not evaluation or iteration >= 15:
					line = self.getNewLine(PoS, editedLine.strip(), transformedText, rhymeScheme, meter, currentTheme, theme, lineNumber)
					evalution = self.eval.evaluateLine(line)
					iteration += 1
				print(iteration)
				transformedText.append(line)
				print(line)
			print(currentTheme)
			for line in transformedText:
				print(line)
			print("")
			#pickle.dump(transformedText, open(str(theme)+"text.pickle", "wb"))

if __name__ == '__main__':
		print "Loading Alvin..."
		a = Alvin()
		print "Running..."
		a.run()
