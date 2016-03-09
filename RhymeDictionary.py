import os
import re

class RhymeDictionary:

	def __init__(self):
		self.rhymeFilePath = 'rhyme_data/'
		self.wordList = {}

	def loadRhymeFiles(self):
		alphabet = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','misc']
		for letter in alphabet:
			self.loadRhymeFile(letter)

	def loadRhymeFile(self, letter):
		f = open(os.path.abspath(self.rhymeFilePath) + "/b-rhymes_" + letter + ".txt")
		for line in f.readlines():
			segments = line.split('-')
			word = segments[0]
			syllables = segments[1].split(',')
			wordObject = Word(word, syllables, [])
			rhymes_scores = segments[2].replace('\n','').split(',')
			if len(rhymes_scores) > 1:
				for rhyme_score in rhymes_scores:
					rhyme, score = rhyme_score.split('/')
					wordObject.addRhyme(rhyme, score)
			self.wordList[word] = wordObject
			
	def printDictionary(self):
		for key in self.wordList.keys():
			wordObject = self.wordList.get(key)
			print key, wordObject.getSyllables(), wordObject.getRhymes()

	def getSyllables(word):
		wordObject = self.wordList[word]
		return wordObject.getSyllables()

	def getRhymes(self, word):
		wordObject = self.wordList[word]
		rhymes_dict = wordObject.getRhymes()
		rhymes = []
		for RhymeObject in rhymes_dict:
			rhymes.append(RhymeObject.getRhyme())
		return rhymes

class Word:

	def __init__(self, word, syllables, rhymes):
		self.word = word
		self.syllables = syllables
		self.rhymes = rhymes

	def addRhyme(self, rhyme, score):
		self.rhymes.append(Rhyme(rhyme, score))

	def addSyllables(self, syllables):
		self.syllables = syllables

	def getWord(self):
		return self.word

	def getSyllables(self):
		return self.syllables

	def getRhymes(self):
		return self.rhymes


class Rhyme:

	def __init__(self, rhyme, score):
		self.rhyme = rhyme
		self.score = score

	def getRhyme(self):
		return self.rhyme

	def getScore(self):
		return self.score


if __name__ == '__main__':
	d = RhymeDictionary()
	d.loadRhymeFiles()
#	print 'done'
#	print d.getRhymes('light')

