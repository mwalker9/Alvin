from stop_words import get_stop_words

class StopWords(object):
	"""a class that removes stop words from a file and provides a replacement file"""

	def __init__(self):
		# download the stop words from the python library
		self.stopWords = get_stop_words('en')
		
	# the actual method that removes the stop words and creates a replacement file	
	def deleteStopWords(self, pathSource, pathDest, separator):
		
		temp_line = ""
		
		with open(pathSource, 'r') as f:
			for line in f:
				text = line.strip().split(separator)
				for i, word in enumerate(text):
					if word not in sw:
						temp_line += word + separator
				
				# delete out last separator
				temp_line = temp_line[:-1]
				temp_line += '\n'
	
		f = open(pathDest, 'w')
		f.write(temp_line)
		f.close()
