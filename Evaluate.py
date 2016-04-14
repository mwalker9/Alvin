# evaluates text as it comes in
# will want to bring in text from different sources
import nltk
from nltk.parse.stanford import StanfordDependencyParser
import os
import Node
import Tree
reload(Node)
reload(Tree)
from copy import copy
import cPickle
from time import sleep

################################
# to do's                     
#	replace pronouns with proper nouns
#	concatenate proper nouns
#	ACL's!!!
# 	

# takes the human coded rules and finds relevant paths for them
# accumulates these paths in a pickled file
# typically, the path has been toyData.txt
def train(path):

	f = open(path, 'r')
	
	eval = Evaluator()	
	
	# clear out the previous file
	fR = open(eval.path, 'w')
	fR.close()
		
	for i, line in enumerate(f): # 78,79,57,58
		text = line.strip().split('|')
		# each path learned will be stored
		eval.learnRules(text)
		
	f.close()
	
	# pickle termD
	eval.termD.setdefault('root', 'relationship')
	f = open(eval.tree.termDPath, 'w')
	cPickle.dump(eval.termD, f)
	f.close()

# creates rules for the database
def validateText(textPath, pathsPath, rulePath):

	eval = Evaluator()
	f = open(textPath, 'r')
	rules = eval.parsePaths(pathsPath)
	
	for i, line in enumerate(f):
	
		line = line.strip()
		print line	
		
		# first derive the tree
		result = eval.dependencyParser.raw_parse(line)
		dependencies = result.next()
		eval.dependencies = list(dependencies.triples())
				
		# build the tree
		eval.buildTrees(eval.dependencies)
	
		# now combine compounds
		eval.combineCompounds()
		eval.prependAdjectiveWrapper()
		
		# creates the new list of dependencies
		eval.treeToDependencies()
		
		for rule in rules:	
			print rule
			eval.parseRules(rule)
		sleep(2)
	f.close()
	
	# accumulate rules into a 'database'
	f = open(rulePath, 'w')
	cPickle.dump(eval.ruleList, f)
	f.close()
	

	
		
def fakeInspirationToToyData():
	path = '.\InspirationSet\\FakeInspirationII.txt'
	f = open(path, 'r')
	
	text = ''
	
	for line in f:
		text += line.split('|')[0] + '\n'
		
	f.close()
	
	path = '.\InspirationSet\\toyData.txt'
	f = open(path, 'w')
	f.write(text)
	f.close()


def defineRules(path):
	
	eval = Evaluator()
	text = eval.parseData(path)

	#v,d = eval.textToRules(sent)
	#return v, d

	valuations = []
	
	for i, line in enumerate(text): # 78,79,57,58
		f = open('.\InspirationSet\FakeInspirationII.txt', 'ab')
		needsCorrection = True
		moreRules = True		
		while needsCorrection:
			print line
			resp = raw_input('Skip? (y/n): ')
			if resp.lower() == 'y':
				f.close()
				needsCorrection = False
				moreRules = False
				continue
				
			find = raw_input('What to replace: ')
			if find == '':
				needsCorrection = False
				continue
			# this would be the case where it does not
			repl = raw_input('With what? ')
			line = line.replace(find, repl)	
			
		# first derive the tree
		result = eval.dependencyParser.raw_parse(line)
		dependencies = result.next()
			
		eval.dependencies = list(dependencies.triples())	
				
		# build the tree
		eval.buildTrees(eval.dependencies)

		# now combine compounds
		eval.combineCompounds()
		eval.prependAdjectiveWrapper()
			
		# creates the new list of dependencies
		eval.treeToDependencies()			
		
		for tup in eval.dependencies:
			print tup
			
		while moreRules:
			rule = raw_input('Create a rule: ')
			if rule == '':
				moreRules = False
				f.write(line + '\n')
				f.close()
				continue
			line = line + "|" + rule
		
		
		#v, d = eval.textToRules(line)
		#return v, d
		#print dependencies
		#print i, rule
		#valuations.extend(rule)
		#return line, dependencies, rule
	
	#return valuations

class Evaluator(object):
	
	def __init__(self):
		self.data = None
		self.rules = []
		self.tree = None
		self.nodeList = []
		self.landmarks = []
		self.s = None
		self.t = None
		self.dependencies = []
		self.rebuiltDependencies = []
		self.minPath = []
		self.metaPath = []
		self.minPathLength = 999
		self.path = '.\InspirationSet\Paths.txt'
		self.termDPath = '.\InspirationSet\termD.txt'
		self.termD = {}
		self.ruleList = []
		self.rulePath = '.\InspirationSet\Rules.txt'
		
		# dependency parsers to build parse tree
		#os.environ['JAVA_HOME'] = 'C:/Program Files (x86)/Java/jre1.8.0_65/bin/java.exe'
		self.path_to_jar = 'stanford-parser-full-2015-12-09/stanford-parser.jar'
		self.path_to_models_jar = 'stanford-parser-full-2015-12-09/stanford-parser-3.6.0-models.jar'
		self.dependencyParser = StanfordDependencyParser(path_to_jar=self.path_to_jar, path_to_models_jar=self.path_to_models_jar)
		
	# evaluates the line
	def evaluateLine(self, line):
		
		# clear previous data
		self.ruleList = []
		
		self.processLine(line)
		
		#for i in self.dependencies:
		#	print i
		
		# upload paths
		paths = self.parsePaths(self.path)
		
		for path in paths:
			self.parseRules(path)
			
		# upload known rules
		# observe that we do not need to upload these rules. They were never stored to memory
		f = open(self.rulePath, 'r')
		knownRules = cPickle.load(f)
		f.close()
		
		for i in self.ruleList:
			if i in knownRules:
				#print i
				#print 'hurray!'
				return True
		return False
		
		
	
	# builds and modifies the dependencies
	def processLine(self, line):
		# first derive the tree
		result = self.dependencyParser.raw_parse(line)
		dependencies = result.next()
		self.dependencies = list(dependencies.triples())
				
		# build the tree
		self.buildTrees(self.dependencies)
		
		# now combine compounds
		self.combineCompounds()
		self.prependAdjectiveWrapper()
		
		# creates the new list of dependencies
		self.treeToDependencies()
			
		
	# creates the list of dependencies from the tree
	def treeToDependencies(self):
	
		self.rebuiltDependencies = []
		
		# start at root and move down
		self.nodeToTuple(self.tree.root)
		
		self.dependencies = self.rebuiltDependencies
		
	# creates a list tuple for the node	
	def nodeToTuple(self, Node):
	
		if len(Node.children) == 0:
			# we are done with this node
			return
			
		# create governor values
		g = (Node.value, Node.type)
	
		# depends on the children
		for child in Node.children:
			
			r = child.edge.relationship
			d = (child.value, child.type)
			self.rebuiltDependencies.append((g, r, d))
			self.nodeToTuple(child)
		
	def parsePaths(self, rulesPath):
	
		paths = []
		
		f = open(rulesPath, 'r')
		
		eof = False
		
		while not eof:
			
			try:
				paths.append(cPickle.load(f))
			except:
				eof = True
				
		f.close()
		
		return paths
		
	# uploads data from different sources
	def parseData(self, path):
		f = open(path, 'r')
		text = f.read()
		
		# delete out hyperlinks and references
		procText = ''
		ignore = False
		punctuation = ['.', ',', ';', '-', "'"]
		for i in text:
			if (i.isalnum() or i.isspace() or i in punctuation) and not ignore:
				procText += i
			# need to ignore references
			if i == '[' or i =='(':
				ignore = True
			elif i == ']' or i == ')':
				ignore = False

		text = procText.split('. ')
		
		data = []
		for line in text:
			# double end of lines means there is a break in sentences
			line = line.split('\n\n')
			for sent in line:
				sent = sent.replace('\n', '')
				if sent != '':
					data.append(sent)
		
		return data
		
	def createTree(self, dependencies):
		
		# find the root first
		idx, root = self.findRoot(dependencies)

		# build the tree	
		self.tree = Tree.Tree(root, dependencies, idx)
		self.tree.buildTree()
		
	def findRoot(self, dependencies):
		# finds the root of the tree by find the head that has no dependencies
		for i, (g1, r1, d1) in enumerate(dependencies):
			isDependent = False
			for (g2, r2, d2) in dependencies:
				if g1[0] == d2[0]:
					isDependent = True
					
			if not isDependent:
				return i, g1[0]
				
	def textToRules(self, rawText):	
		valuations = []
		# 3 step process	
		#	1. Convert raw text to dependency graph
		#	2. Convert dependency graph to cfg
		#	3. Extract valuations
		#	4. Convert valuations to 1st order logic
		
		# 1. Convert raw text to dependency graph
		# http://stackoverflow.com/questions/7443330/how-do-i-do-dependency-parsing-in-nltk/33808164#33808164
		#	First parse text into atomic dependencies		
		result = self.dependencyParser.raw_parse(rawText)
		# list of dependency for each word
		dependencies = result.next()
		self.dependencies = list(dependencies.triples())
		
		#return valuations, dependencyList
		
		#print dependencyList
		self.buildTrees(self.dependencies)
		
		self.combineCompounds()
		self.prependAdjectiveWrapper()
		
		# creates the new list of dependencies
		self.treeToDependencies()
		
		# a series of joining common areas of the graph.
		# we can learn these!!! (learn common combinations from training data)
		self.parseRules(self.dependencies)
	
		#self.rootParse(dependencyList)
		
		# Extract valuations
		#valuations = self.extractVerbs(dependencyList)
		
	# combines all compounds	
	def combineCompounds(self):
		
		# the final compound will take the POS tag of the parent 
		self.addCompound(self.tree.root)
		
	# the node takes value from its children with compound relationships
	def addCompound(self, Node):
		
		if len(Node.children) == 0:
			# nothing to do here
			return
			
		popL = []
		s = ''
		for i,child in enumerate(Node.children):
			
			# check to see if it is a compound
			if child.edge.relationship == 'compound':
				s += child.value + '_'
				
				popL.append(i)
				
			else:
				self.addCompound(child)
				
		popL.reverse()
		
		# remove compound children
		for i in popL:
			Node.children.pop(i)
			
		# give the node its full name
		Node.value = s + Node.value
		
	# prepends adjectives
	def prependAdjectiveWrapper(self):
		
		self.prependAdjective(self.tree.root)
	
	# prepends JJ to each node from its children
	def prependAdjective(self, Node):
		if len(Node.children) == 0:
			# nothing to do here
			return
			
		popL = []
		s = ''
		for i,child in enumerate(Node.children):
			
			# check to see if it is a compound
			if child.type == 'JJ':
				s += child.value + '_'
				
				popL.append(i)
				
			else:
				self.prependAdjective(child)
				
		popL.reverse()
		
		# remove compound children
		for i in popL:
			Node.children.pop(i)
			
		# give the node its full name
		Node.value = s + Node.value
		
		
	def concatenateCompounds(self, dependencies, governor, parent):
		# we want to return the last compound
		window = False
		compound = False
		for i,(g, r, d) in enumerate(dependencies):
		
			if window == False and g[0] == parent and d[0] == governor:
				# we can start to consider compounds
				window = True
			
			elif window == True and g[0] != parent and d[0] == governor:
				# we have come across a different node with the same value
				window = False
				# we are done
				break
			
			elif window == True and g[0] == governor and r == 'nummod':
				compound = d[0]
		
			elif window == True and g[0] == governor and r == 'compound':
				compound = d[0]
			
			# adjective
			elif window == True and g[0] == governor and r == 'amod':
				compound = d[0]
		
		return compound		
		
	# builds both the main tree and the substructures	
	def buildTrees(self, dependencies):		
	
		# find the root
		self.createTree(dependencies)
		
		# build substructures for xcomp
		#self.parseXComp(dependencies)		
	
	def rootParse(self, dependencies):

		# write rules to a document
		f = open('.\Rules.txt', 'ab')
		
		# loop through and find triangles
		for i, (g, r, d) in enumerate(dependencies):
			if g[1][0] == 'V':
				
				# verb nodes
				vNodes = set([])
				# noun nodes
				nNodes = set([])
				
				self.tree.findNodeWrapper(g[0], g[1], '', '', 'buildtree')
				n = self.tree.foundNode
				
					
				# this is the case where the node has already been evaluated
				if n == None:
					continue
				# look for rules with children
				for child in n.children:
					#print 'looking for children of', g[0]
					if child.type[:2] == 'NN' or child.type == 'PRP' or child.type == 'WP':
						# we can never use this node for another purpose
						#child.checked = True
						nNodes.add(child)
					elif child.type[:1] == 'V':
						# these are very interesting
						vNodes.add(child)
						
				print g[0], len(nNodes), len(vNodes)
				
				# pull data from nodes
				nNL, vNL, tNL, rNL = self.organizeNodes(nNodes, dependencies)
				nVL, vVL, tVL, rVL = self.organizeNodes(vNodes, dependencies)				
						
				if len(nNL) == 1:
					# extract the node
					#n = nodes.pop()
					pass
				
					#print g[0] + "(" + n.value + ")", n.edge.relationship				
						
				# we can look for certain combinations of nouns and relationships
				elif len(nNL) >= 2:
				
					# classic structure of a subject and direct object
					if 'nsubj' in rNL and 'dobj' in rNL:
						rule = g[0] + "(" + vNL[rNL.index('nsubj')] + ", " + vNL[rNL.index('dobj')] + ")"
						f.write(rule + '\n')
						print rule
						
					elif 'nsubj' in rNL and 'xcomp' in rNL:
						rule = g[0] + "(" + vNL[rNL.index('nsubj')] + ", " + vNL[rNL.index('xcomp')] + ")"
						f.write(rule + '\n')
						print rule	

					elif 'nsubj' in rNL and 'nmod' in rNL:
						rule = g[0] + "(" + vNL[rNL.index('nsubj')] + ", " + vNL[rNL.index('nmod')] + ")"
						f.write(rule + '\n')
						print rule	
						
					elif 'nsubjpass' in rNL and 'nmod' in rNL:
						
						'''
						if 'auxpass' in rVL:
							rule = vVL[rVL.index('auxpass')] + '_' + g[0] + "(" + vNL[rNL.index('nsubjpass')] + ", " + vNL[rNL.index('nmod')] + ")"
							f.write(rule + '\n')
							print rule	
						'''
						
						rule = g[0] + "(" + vNL[rNL.index('nmod')] + ", " + vNL[rNL.index('nsubjpass')] + ")"
						f.write(rule + '\n')
						print rule	

				if len(nVL) > 0:
					# right now, we are just looking for conjunctions
					
					# conjunction					
					
					if 'conj' not in rVL:
						# save the trouble of looking for anything else for now. Maybe need something later!!!
						continue
						
					# there may be multiple conjunctions
					
					for verbNode in nVL:
					
						if verbNode.edge.relationship == 'xcomp':
							
							if 'nsubj' in rNL:
								rule = g[0] + "_" + self.tree.xcompD[verbNode.value]['verbConj'] + \
								"(" + vNL[rNL.index('nsubj')] + ", " + self.tree.xcompD[verbNode.value]['dobjConj'] + ")"
					
						elif verbNode.edge.relationship == 'conj':
							#print 'right here', verbNode.value
							#print rNL
						
							value = ''; adverb = ''
							for child in verbNode.children:
								if child.edge.relationship == 'dobj' or child.edge.relationship == 'xcomp':
									value = child.value
									compound = self.concatenateCompounds(dependencies, value, child.parent)
									if compound != False:
										value = compound + ' ' + value
										
								elif child.edge.relationship == 'advmod':
									adverb = child.value
							
							# go back and use the parent nmod
						
							if value == '':
								if 'nmod' in rNL:
									value = vNL[rNL.index('nmod')]
								elif 'xcomp' in rNL:
									value = vNL[rNL.index('xcomp')]
								
						
							if 'nsubj' in rNL:
								#		verb joined to head				subject of head verb			
								rule = verbNode.value + "(" + vNL[rNL.index('nsubj')] + ", " + value + ")"
								f.write(rule + '\n')
								print rule
								
							elif 'nsubjpass' in rNL:
								#		verb joined to head				subject of head verb			
								rule = verbNode.value + "(" + value + ", " + vNL[rNL.index('nsubjpass')] + ")"
								f.write(rule + '\n')
								print rule				
					
						
					
			# very simple rule for adjectives
			'''
			elif d[1] == 'JJ':
				# find any compounds
				newValue = ''
				comp = self.concatenateCompounds(dependencies, g[0])
				if comp == False:
					newValue = g[0]
				else:
					newValue = comp + " " + g[0]		
				
				rule = d[0] + "(" + newValue + ")"
				f.write(rule + '\n')
				print rule	
			'''
		f.close()
				
	# pops the nodes out of the set and also creates lists of their data
	def organizeNodes(self, nodeSet, dependencies):
		
		# structures to hold node data
		nodeL = []; valueL = []; typeL = []; relationL = []
		
		while len(nodeSet) > 0:
			n = nodeSet.pop()
			
			# find any compounds
			comp = self.concatenateCompounds(dependencies, n.value, n.parent)
			if comp == False:
				pass
			else:
				n.value = comp + " " + n.value	

			# switch out proper nouns
			# !!!
			
			valueL.append(n.value)
			typeL.append(n.type)
			relationL.append(n.edge.relationship)
			nodeL.append(n)
			
		return nodeL, valueL, typeL, relationL
		
	# parses all xcomps	
	def parseXComp(self, dependencies):
		
		for i, (g, r, d) in enumerate(dependencies):
			
			if r == 'xcomp':
				
				# we want the dependent
				self.tree.findNodeWrapper(d[0], d[1], g[0], r, 'substructures')
				n = self.tree.foundNode
				self.tree.xcompD.setdefault(d[0], {})
				
				if n.type[0] == 'V':
					self.tree.xcompD.setdefault(n.value, {'verbConj' : '', 'dobjConj' : ''})
					
					for child in n.children:
						if child.edge.relationship == 'dobj':
							self.tree.xcompD[n.value]['dobjConj'] = child.value
						elif child.edge.relationship == 'nmod':
							self.tree.xcompD[n.value]['verbConj'] = child.value
							
	def findParent(self, dependencies, (gV, gT), i):
	
		for j, (g, r, d) in enumerate(dependencies[:i]):
			
			# it can only be the parent
			if d[0] == gV and d[1] == gT:
				return g[0], g[1], r
				

	def parseRules(self, funcList):
	
		# load the termD
		self.tree.loadTermD()
		
		self.tree.rule = ''
		termList = []
		
		try:
	
			self.tree.parseFunctions(self.tree.root, funcList, termList)
		
			if self.tree.rule != '':
				#print self.tree.rule
				self.ruleList.append(self.tree.rule)
		except:
			pass
		
	# learns rules in the form of a list of tuples
	def learnRules(self, line):
	
		print line[0]
	
		self.processLine(line[0])
		
		for i in self.dependencies:
			print i
		
		# record dependents for the termD
		for (g, r, d) in self.dependencies:
			self.termD.setdefault(d[1], 'type')
			self.termD.setdefault(r, 'relationship')		
		
		# find path for rules
		for rule in line[1:]:
		
			print rule
			
			rule = rule.replace(')','').split('(')
			predicate = rule[0]
			items = rule[1].split(',')
			
			sub = None; dob = None
			if len(items) == 1:
				sub = items[0]	
			else:
				sub = items[0]
				dob = items[1]
			# go from sub to predicte to dob
			# start from end of predicate and work towards the front
			#print predicate, sub, dob
			
			self.landmarks = self.createString(predicate, sub, dob)
			
			# clear nodeList
			self.nodeList = []
			
			#print self.landmarks
			
			self.parseLandmarks(self.tree.root, self.landmarks, [])
			self.developMap()
			
			f = open(self.path, 'ab')
			cPickle.dump(self.metaPath, f)
			f.close()
			print self.metaPath
		
	def createString(self, predicate, sub, dob):
		
		# list of tuples
		# (word, specific token that needs to be substituted)
		l = []
		
		if dob != None:
			for i in dob.split():
				tup = (i, 'relationship')
				l.append(tup)
			
		predicateList = predicate.split('&')
		# we will approach in reverse order
		predicateList.reverse()
		
		for i in predicateList:
			tup = (i, 'type')
			l.append(tup)
			
		for i in sub.split():
			tup = (i, 'relationship')
			l.append(tup)
			
		#print l
			
		return l
			
	def parseLandmarks(self, Node, landmarks, visitedNodes):
	
		# a multi-agent approach to finding the nodes
		
		
		# note the node as being visited
		visitedNodes.append(Node)
	
		if len(self.nodeList) == len(self.landmarks):
			# this is the ideal situation
			return
			
		#print Node.value, landmarks[0]
	
		# check to see if we have arrived at correct node
		if landmarks[0][0] == Node.value:
		
			if Node not in self.nodeList:
				self.nodeList.append(Node)
			
			# find whether the tuple requires a relationship or type
			
			if landmarks[0][1] == 'relationship':
				print 'relationship'
				print "(", Node.value, ", ", Node.edge.relationship, ")"			
								
			elif landmarks[0][1] == 'type':
				print 'type'
				print "(", Node.value, ", ", Node.type, ")"
				
			else:
				print 'we are in trouble!'
			
				
			# continue to parse the landmarks
			# search down
			for child in Node.children:
				# you can go back to a parent, but not back to a child
				# note that the search will die here if there are still landmarks to search for but no children
				#															 you can now search anywhere again
				self.parseLandmarks(child, copy(landmarks[1:]), [])
				
			# search up
			self.parseLandmarks(Node.parent, copy(landmarks[1:]), [])
			
		else:
			# consume the node
			# this will always be a relationship
			
			# continue to parse the landmarks
			# search down
			for child in Node.children:
				if child not in visitedNodes:
					self.parseLandmarks(child, copy(landmarks), copy(visitedNodes))
				
			# search up
			self.parseLandmarks(Node.parent, copy(landmarks), copy(visitedNodes))
			
	# creates a map that defines the shortest route between each node and the qualities of the nodes
	def developMap(self):
	
		# initiate the minPath
		if self.landmarks[0][1] == 'relationship':
			# note this in the termD
			self.metaPath = [(self.nodeList[0].edge.relationship, 'down', 'node')]
			
		elif self.landmarks[0][1] == 'type':
			# note this in the termD
			self.metaPath = [(self.nodeList[0].type, 'down', 'node')]				
				
		else:
			print 'we are in big trouble!'
	
		# find shortest path between each node
		for i, node in enumerate(self.nodeList[:-1]):		
			
			self.minPath = []
			self.s = node
			self.t = self.nodeList[i+1]
			self.minPathLength = len(self.dependencies) + 1
			
			# start with the first type/relationship and direction (which will always be down because it comes from the root)
			self.findShortestPath(self.s.parent, self.t, copy(self.minPath), 'up')
			for child in self.s.children:
				self.findShortestPath(child, self.t, copy(self.minPath), 'down')
			
			self.metaPath.extend(self.minPath)
			
	def findShortestPath(self, sNode, tNode, map, direction):
	
		# ending condition
		if sNode == tNode and len(map) < self.minPathLength:
			#print 'found it'
		
			# index into the nodelist to find the relationship/type
			if self.landmarks[self.nodeList.index(sNode)][1] == 'relationship':
				map.append((sNode.edge.relationship, direction, 'node'))
				
			elif self.landmarks[self.nodeList.index(sNode)][1] == 'type':
				map.append((sNode.type, direction, 'node'))
			
			else:
				print 'we are in big trouble!'
			
			self.minPathLength = len(map)
			self.minPath = map
			return
			
		# another ending condition
		elif len(map) >= self.minPathLength or len(sNode.children) == 0 or sNode.value == 'root':
			return
			
		elif direction == 'down':
		
			# we still need to append the relationship
			map.append((sNode.edge.relationship, direction))
			
			# we can afford to do a breath-first search
			for child in sNode.children:
				self.findShortestPath(child, tNode, copy(map), 'down')
			
		elif direction == 'up':
		
			# we still need to append the relationship
			map.append((sNode.edge.relationship, direction))
			
			# we can afford to do a breath-first search
			for child in sNode.children:
				self.findShortestPath(child, tNode, copy(map), 'down')
				
			self.findShortestPath(sNode.parent, tNode, copy(map), 'up')
			
		else:
			print 'we are in big trouble!'
			
		
		
	
