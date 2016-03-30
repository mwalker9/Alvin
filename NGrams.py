########### Python 2.7 #############
import httplib, urllib, base64, json

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
		conn.close()
	except Exception as e:
		print("[Errno {0}] {1}".format(e.errno, e.strerror))
		return -1
	parsed_json = json.loads(data)
	results = parsed_json["results"]
	finalResults = []
	for map in results:
		newMap = {}
		newMap["word"] = map["word"]
		newMap["probability"] = map["probability"]
		finalResults.append(newMap)
	return finalResults
