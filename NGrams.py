########### Python 2.7 #############
import httplib, urllib, base64, json
import time
import copy
import numpy as np

def generateBody(phrase, possibleWords):
	queries = []
	for word in possibleWords:
		query = {}
		query["words"] = phrase
		query["word"] = word
		queries.append(query)
	return json.dumps(
	{
		"queries": queries
	}
	)
		
def getProbabilities(phrase, possibleWords, order=5):
	if len(possibleWords) == 0:
		print("length is zero!!")
		return []
	key = ""
	with open("key.txt", "r") as f:
		for line in f:
			key = line
	
	headers = {
		# Request headers
		'Content-Type': 'application/json',
		'Ocp-Apim-Subscription-Key': key,
	}
	
	model = "body"
	
	params = urllib.urlencode({
		# Request parameters
		'model': model,
		'order': order,
	})
	body = generateBody(phrase, possibleWords)
	try:
		conn = httplib.HTTPSConnection('api.projectoxford.ai')
		conn.request("POST", "/text/weblm/v1.0/calculateConditionalProbability?%s" % params, body, headers)
		response = conn.getresponse()
		data = response.read()
		if response.status == 429:
			parsed_json = json.loads(data)
			message = parsed_json["message"]
			str = message
			seconds = [int(s) for s in str.split() if s.isdigit()]
			if(len(seconds) != 1):
				raise "Badness"
			seconds = seconds[0]
			print("Sleeping "+str(seconds)+" seconds")
			time.sleep(seconds)
			return getProbabilities(phrase, possibleWords, order=order)
		elif response.status == 403:
			print("Quota has been depleted.")
		conn.close()
	except Exception as e:
		print("Error occurred in NGrams")
		return -1
	
	parsed_json = json.loads(data)
	try:
		results = parsed_json["results"]
	except KeyError:
		print("Error occurred")
		print(data)
		return -1000
	finalResults = []
	for map in results:
		newMap = {}
		newMap["word"] = map["word"]
		newMap["probability"] = map["probability"]
		finalResults.append(newMap)
	return finalResults
	
def getNGramProbabilities(currentLine, possibleWords):
	if currentLine == "":
		return np.ones(len(possibleWords)) / float(len(possibleWords))
	numberOfWords = len(currentLine.split())
	numberToTakeOffFront = max(0, numberOfWords-4)
	phrase = copy.copy(currentLine)
	for i in range(numberToTakeOffFront):
		phrase = phrase.split(' ', 1)[1]
	arrOfMaps = getProbabilities(phrase, possibleWords)
	probabilities = []
	for word in possibleWords:
		found = False
		for map in arrOfMaps:
			if map["word"] == word and not found:
				probabilities.append(np.exp(map["probability"]))
				found = True
		if not found:
			probabilities.append(0)
	return probabilities/sum(probabilities)
	
