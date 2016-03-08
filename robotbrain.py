import argparse
import word2vec
import numpy as np
import re

class RobotBrain:

	# Initializes the robot brain
	def __init__(self):
		self.args = None
		self.parse_arguments()
		self.key_error_message = "KeyError: Word does not exist in Word2vec."
		self.number_of_results = 10
		self.verbose = False
		self.help = "Options:\n\tEnter a single word to return top similar words. Example: \'man\'\n\tEnter a series of \"positive\" and \"negative\" words. Example: \'king woman -man\'\n\tEnter two words separated by a \'v\' to get the distance between words. Example: \'woman v man\'\n\tEnter \'n=xx\' to set the number of results. Example: \'n=30\'\n\tEnter \'verbose=true\' (or false) to return the vector numbers as well. Alternative: \'v=true\'\n\tEnter a word (or words) and 't=x' to get a list of words of a particular part-of-speech. Example: \'man t=N\' or \'pale woman t=VB\'\n\tEnter \'--help\' for help."
		self.tag_list = ['CC', 'CD', 'DT', 'EX', 'FW', 'IN', 'JJ', 'JJR', 'JJS', 'LS', 'MD', 'NN', 'NNS', 'NNP', 'NNPS', 'PDT', 'POS', 'PRP', 'PRP$', 'RB', 'RBR', 'RBS', 'RP', 'SYM', 'TO', 'UH', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'WDT', 'WP', 'WP$', 'WRB']
		self.load_model()
		self.load_tags()

	# Parses input arguments
	def parse_arguments(self):
		parser = argparse.ArgumentParser(prog='Robot Brain', description='A brain for robots', add_help=True)
		parser.add_argument('-m', '--model_location', type=str, default='wikipedia_articles.bin', action='store', help='Specify the location of the model file for Word2vec')
		parser.add_argument('-t', '--tags_location', type=str, default='word_tag_distributions.txt', action='store', help='Specify the location of the POS tag dictionary file')
		args = parser.parse_args()
		self.model_location = args.model_location
		self.tags_location = args.tags_location

	# Loads the model into memory
	def load_model(self):
		print "Loading model..."
		self.model = word2vec.load(self.model_location)
		print "Number of results currently set to: ", self.number_of_results

	# Loads the POS tag dictionary into memory
	def load_tags(self):
		print "Loading POS tags..."
		self.tag_dictionary = {}
		tag_file = open(self.tags_location, 'r')
		for line in tag_file:
			pieces = line[:-1].split('.')
			word = pieces[0]
			tag_list = pieces[1].split('-')
			tag_list_int = []
			for tag in tag_list:
				tag_list_int.append(int(tag))
			self.tag_dictionary[word] = tag_list_int
		print "Loaded in " + str(len(self.tag_dictionary.keys())) + " keys"

	# Runs the main query loop
	def query_brain(self):
		print self.help, "\n"
		# Run forever
		while(True):
			input_string = raw_input("Enter a word or a series of words separated by spaces (add - for subtracted): ")
			try:
				print self.handle_query(input_string)
			except Exception:
				print "Well that didn't work."
			print ''

	# Handles a single query
	def handle_query(self, input_string):
		words = input_string.split(' ')
		# If the input only consists of a single word (no spaces)...
		if len(words) == 1:
			word = words[0].lower()
			# If the input starts with 'n=' (if the input is 'n=xx')
			if word.startswith('n='):
				number_as_string = word[2:]
				self.number_of_results = int(number_as_string)
				return "Number of results is now: ", self.number_of_results
			# If the input is changing verbose to true
			elif word == "verbose=true" or word == "v=true":
				self.verbose = True
				return "Verbose is now: " + self.verbose
			# If the input is changing verbose to false
			elif word == "verbose=false" or word == "v=false":
				self.verbose = False
				return "Verbose is now: " + self.verbose
			# If help is needed
			elif word == '--help':
				return self.help
			elif 'tag=' in word:
				word = word[4:]
				if self.tag_dictionary.has_key(word):
					return self.tag_dictionary[word]
			elif 'pop=' in word:
				return self.get_popularity(word[4:])
			# If the input is a single word (ie 'man')
			else:
				try:
					#print self.get_POS_list(self.format_output(self.get_results_for_word(word)))
					return self.format_output(self.get_results_for_word(word))
				except KeyError:
					return self.key_error_message
		# If the input is more than a single word...
		else:
			# If the input is two words separated by a 'v' (ie 'man v woman)
			if words[1] == 'v' or words[1] == 'V':
				first_word = words[0].lower()
				second_word = words[2].lower()
				cosine_similarity = self.get_cosine_similarity(first_word, second_word)
				return cosine_similarity
			# If the input's last argument is a part of speech request (ie 't=N', 't=VB')
			elif words[len(words) - 1].startswith('t='):
				pos_tag = "_" + words[len(words) - 1][2:]
				pos_results = 10
				pos_matches = []
				word = ''
				# If the input consists of a single word and a pos request (ie 'man t=V')
				if len(words) == 2:
					word = words[0].lower()
				# If the input consists of many words and a pos request (ie 'man -woman t=V')
				else:
					words_without_pos_request = words[:-1]
					positives, negatives = self.get_positives_and_negatives(words_without_pos_request)
					word = self.format_output(self.get_results_for_words(positives, negatives))[0]
					print "This is the result of the word math:", self.format_output(self.get_results_for_words(positives, negatives))
					print "This is the word:", word
				while len(pos_matches) < self.number_of_results:
					pos_matches = self.get_POS_results(word, pos_tag, pos_results)
					if len(pos_matches) < self.number_of_results:
						pos_results *= 2
					else:
						return pos_matches
			# If the input is word math (ie 'man -woman')
			else:
				positives, negatives = self.get_positives_and_negatives(words)
				try:
					return self.format_output(self.get_results_for_words(positives, negatives))
				except KeyError:
					return self.key_error_message

	# Takes a list of words (ie 'king woman -man') and separates them into two lists (ie '["king", "woman"], ["man"]')
	def get_positives_and_negatives(self, words):
		positives = []
		negatives = []
		for x in xrange(len(words)):
			word_arg = words[x]
			if word_arg.startswith('-'):
				negatives.append(word_arg.lower()[1:])
			else:
				positives.append(word_arg.lower())
		return positives, negatives

	# Returns the cosine similarity between two words
	def get_cosine_similarity(self, first_word, second_word):
		return np.dot(self.model[first_word], self.model[second_word])/(np.linalg.norm(self.model[first_word])* np.linalg.norm(self.model[second_word]))

	# Returns the results of entering a single word into word2vec (returns similar words)
	def get_results_for_word(self, word):
		indexes, metrics = self.model.cosine(word, n=self.number_of_results)
		similar_words = self.model.generate_response(indexes, metrics).tolist()
		return similar_words

	# Returns the results of entering a list of positive and negative words into word2vec
	def get_results_for_words(self, positives, negatives):
		indexes, metrics = self.model.analogy(pos=positives, neg=negatives, n=self.number_of_results)
		results = self.model.generate_response(indexes, metrics).tolist()
		return results

	# Changes the output from a list of tuples (u'man', 80.810027423), ... to a list of single words
	def format_output(self, output):
		if self.verbose:
			return output
		else:
			words = []
			for word_value in output:
				words.append(str(word_value[0]))
			return words

	# Returns a list of the input words with POS tags.
	def get_POS_list(self, word_list):
		pos_list = []
		for word in word_list:
			pos_list.append(self.get_POS_tag(word))
		return pos_list

	# Returns the input word with a POS tag.
	def get_POS_tag(self, word):
		word_spaces = word.split('_')
		pos_list = []
		output = ''
		for single_word in word_spaces:
			pos_list.append(single_word + self.get_most_likely_POS_tag(single_word))
			output += single_word + self.get_most_likely_POS_tag(single_word)
		#print word, pos_list
		tag_list = re.findall(r'_[A-Z$]*', output)

		# This might not work very well. Currently it tags a word-phrase using the last tag in the phrase.

		return word + tag_list[len(tag_list) - 1]

	# Returns the highest tag for a specific word in the tag dictionary.
	def get_most_likely_POS_tag(self, word):
		if self.tag_dictionary.has_key(word):
			distribution = self.tag_dictionary[word]
			most_likely_tag = self.tag_list[distribution.index(max(distribution))]
			if max(distribution) == 0:
				return '_IDK'
			if word == 'haired':
				return '_JJ'
			return '_' + most_likely_tag
		return '_IDK'
		
	# Returns the popularity of a word (according to the number of tags in Wikipedia).
	def get_popularity(self, word):
		if self.tag_dictionary.has_key(word):
			distribution = self.tag_dictionary[word]
			total_count = 0;
			for tag_count in distribution:
				total_count += tag_count
			return total_count
		else:
			return 0

	# Returns a list of the words of a particular part-of-speech closest to the input word
	def get_POS_results(self, word, pos_tag, pos_results):
		pos_matches = []
		indexes, metrics = self.model.cosine(word, pos_results)
		similar_words = self.model.generate_response(indexes, metrics).tolist()
		pos_list = self.get_POS_list(self.format_output(similar_words))
		for pos_word in pos_list:
			#if pos_tag in pos_word:
			if pos_word.endswith(pos_tag):
				pos_matches.append(pos_word)
		pos_matches_clean = []
		for pos_match in pos_matches:
			pos_matches_clean.append(pos_match.replace(pos_tag, ''))
		return pos_matches_clean

if __name__ == '__main__':
	r = RobotBrain()
	r.query_brain()

# examples of proper use:
#man
#king woman -man
#n=40
#man v woman
#--help
#king woman -man t=JJ
#man t=VB
#tag=man
#pop=man
# Run with: python robotbrain.py -m wikipedia_articles.bin -t word_tag_distributions.txt
