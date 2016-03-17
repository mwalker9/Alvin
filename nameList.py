class nameList:
	
	names = set()

	def __init__(self):
		with open("nameList.txt", "r") as f:
			for line in f:
				self.names.add(line.strip().lower())
	
		