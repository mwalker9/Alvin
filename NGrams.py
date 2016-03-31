########### Python 2.7 #############
import httplib, urllib, base64, json
import time

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
