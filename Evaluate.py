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
import numpy as np

################################
# to do's                     
#	replace pronouns with proper nouns
#	concatenate proper nouns
#	ACL's!!!
#	eliminate redundant rules
#	while parsing lines, keep track of count of how many times a rule 'works'
#	That will be the score the tested line gets if it 'passes' 	
#   Notes: When parsing, make the first node 'free'. That is, you can go directly to the direct object without respect to what it is tied to

# takes the human coded rules and finds relevant paths for them
# accumulates these paths in a pickled file
def train(path):

	f = open(path, 'r')
	
	eval = Evaluator()	
	
	# clear out the previous file
	fR = open(eval.path, 'w')
	fR.close()
	
	# record dependents for the termD
		
	for i, line in enumerate(f): # 78,79,57,58
		text = line.strip().split('|')
		# each path learned will be stored
		eval.learnRules(text)
		
	f.close()
	
	# pickle termD
	eval.tree.termD['root'] = 'function'
	f = open(eval.tree.termDPath, 'w')
	cPickle.dump(eval.tree.termD, f)
	f.close()

# creates rules for the database
def validateText(textPath, pathsPath, rulePath):

	eval = Evaluator()
	f = open(textPath, 'r')
	# reset path counts
	eval.pathCounts = np.zeros(len(eval.learnedPaths)) 
	print len(eval.pathCounts)
	
	for i, line in enumerate(f):
	
		
	
		line = line.strip()
		#print line
		
		# there are alot of lines that will not produce a parse tree
		try:
			eval.processLine(line)
			sleep(1)
		except:
			continue
		
		for rule in eval.learnedPaths:	
			#print rule
			eval.parseRules(rule)
		
		if i % 20 == 0:
			print i, 'num rules', eval.pathCounts.sum()	
			# accumulate rules into a 'database'
			f = open(rulePath, 'w')
			cPickle.dump(eval.ruleList, f)
			f.close()
			f = open(eval.pathCountsPath, 'w')
			cPickle.dump(eval.pathCounts, f)
			f.close()
			
		
		sleep(2)
	f.close()
	
	# save the counts for evaluation	
	
		
def fakeInspirationToToyData():
	path = 'C:\Users\jkjohnson\Desktop\Alvin-master\InspirationSet\\PathTrainingData.txt'
	f = open(path, 'r')
	
	text = ''
	
	for line in f:
		text += line.split('|')[0] + '\n'
		
	f.close()
	
	path = 'C:\Users\jkjohnson\Desktop\Alvin-master\\InspirationSet\\toyData.txt'
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
		f = open('C:\Users\jkjohnson\Desktop\Alvin-master\InspirationSet\FinalTrainingData.txt', 'ab')
		
		# first derive the tree
		eval.processLine(line)	
		
		try:
			print eval.dependencies[0]
		except:
			print 'you just may want to skip'
		
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
			
		if not moreRules:
			continue
			
		# first derive the tree
		eval.processLine(line)	
		
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
		self.ruleList = []
		self.rulePath = '.\InspirationSet\Rules.txt'
		self.learnedPaths = self.parsePaths(self.path)		
		self.pathCountsPath = '.\InspirationSet\PathCounts.txt'
		f = open(self.pathCountsPath,'r')
		self.trainingPathCounts = cPickle.load(f)
		self.pathCounts = np.zeros(len(self.learnedPaths))
		
		# load in rules
		f = open(self.rulePath, 'r')
		self.knownRules = cPickle.load(f)
		f.close()
		
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
		
		# reset the  path count numbers
		self.pathCounts = np.zeros(len(self.learnedPaths))
		
		for path in self.learnedPaths:
			#print path
			self.parseRules(path)
			
		score = (self.pathCounts * self.trainingPathCounts).sum()
			
		# upload known rules
		# observe that we do not need to upload these rules. They were never stored to memory
		f = open(self.rulePath, 'r')
		knownRules = cPickle.load(f)
		f.close()
		
		for i in self.ruleList:
			if i in self.knownRules:
				#print i
				score += 100
	
		return score
		
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
		try:
			self.unificationWrapper()
		except:
			print 'unification crashed!'
			
		
		
		# creates the new list of dependencies
		self.treeToDependencies()
		
		#for i in self.dependencies:
		#	print i
			
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
				path = cPickle.load(f)
				if path not in paths:
					paths.append(path)
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
		
	# unifies the {W*} PoS to a noun ancestor and PRP
	def unificationWrapper(self):		
		
		self.unificationPronoun(self.tree.root)
		self.unificationW(self.tree.root)
	
	def unificationPronoun(self, Node):
		pass
		
	def unificationW(self, Node):
	
		if Node.type == 'WP':
			# return node of ancestor whose parent is connected by acl:relcl
			value, type = self.findRelationship(Node, 'acl:relcl')
			Node.value = value; Node.type = type
		elif len(Node.children) == 0:
			pass
		else:
			for child in Node.children:
				self.unificationW(child)
		
	# returns the type and value of a node that is connected to a parent by the specified relationship
	def findRelationship(self, Node, relationship):
			if Node.edge.relationship == relationship:
				return Node.parent.value, Node.parent.type
			else:
				return self.findRelationship(Node.parent, relationship)
			
		
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
		f = open('C:\Users\jkjohnson\Documents\CS 673\Alvin-master\Star Wars Data\Rules.txt', 'ab')
		
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
		
							
	def findParent(self, dependencies, (gV, gT), i):
	
		for j, (g, r, d) in enumerate(dependencies[:i]):
			
			# it can only be the parent
			if d[0] == gV and d[1] == gT:
				return g[0], g[1], r
				

	def parseRules(self, funcList):
	
		f = open(self.tree.termDPath, 'r')
		self.tree.termD = cPickle.load(f)
		f.close()
		
		self.tree.rules = []
		
		
		# free trip to first node
		self.tree.foundNodes = []
		self.tree.findNode(self.tree.root, funcList[0])
		#print len(self.tree.foundNodes)
		if len(self.tree.foundNodes) > 0:
			for Node in self.tree.foundNodes:
				try:
					termList = []
					self.tree.parseFunctions(Node, funcList, termList)
					#print funcList
				except:
					pass
		
		if self.tree.rules != []:
			#print self.tree.rule
			for rule in self.tree.rules:
				self.pathCounts[self.learnedPaths.index(funcList)] += 1
				if rule not in self.ruleList:
					#print 'found!', rule
					self.ruleList.append(rule)
				
		
		
	# learns rules in the form of a list of tuples
	def learnRules(self, line):
	
		print line[0]
	
		self.processLine(line[0])
		
		for i in self.dependencies:
			print i
		
		
		
		for (g, r, d) in self.dependencies:
			self.tree.termD.setdefault(d[1], 'variable')
			self.tree.termD.setdefault(r, 'function')		
		
		# find path for rules
		for rule in line[1:]:
		
			print 'rule',rule
			
			rule = rule.replace(')','').split('(')
			predicate = rule[0].replace('[','').replace(']','')
			items = rule[1].split(', ')
			
			sub = None; dob = None
			if len(items) == 1:
				sub = items[0]	
			else:
				sub = items[0].replace('[','').replace(']','').split(','); sub.append('variable')
				dob = items[1].replace('[','').replace(']','').split(','); dob.append('variable')
			# go from sub to predicte to dob
			# start from end of predicate and work towards the front
			# this helps in traversing the tree. You will be going up instead of down most of the time.
			#print 'sub', sub
			#print 'dob', dob
			
			self.landmarks = self.createString(predicate, sub, dob)
			#print 'landmarks',self.landmarks
			#return
			
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
			l.append(dob)
			
		predicateList = predicate.split('&')
		
		# we will approach in reverse order
		predicateList.reverse()
		
		for i in predicateList:
			i = i.split(',')
			i.append('function')
			l.append(i)
			
		l.append(sub)
			
		return l
			
	def parseLandmarks(self, Node, landmarks, visitedNodes):
	
		# a multi-agent approach to finding the nodes		
		
		# note the node as being visited
		visitedNodes.append(Node)
	
		if len(self.nodeList) == len(self.landmarks):
			# this signals that all nodes have been found
			# this will cause all other agents to cease their search also
			# this is the ideal situation
			# it means all landmarks have been found
			return
	
		# check to see if we have arrived at correct node
		if landmarks[0][0] == Node.value and landmarks[0][1] == Node.type and landmarks[0][2] == Node.edge.relationship:
		
			if Node not in self.nodeList:
				self.nodeList.append(Node)			
				
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
			for child in Node.children:
				if child not in visitedNodes:
					self.parseLandmarks(child, copy(landmarks), copy(visitedNodes))
				
			# search up
			if Node.edge.relationship != 'root':
				self.parseLandmarks(Node.parent, copy(landmarks), copy(visitedNodes))
			
	# creates a map that defines the shortest route between each node and the qualities of the nodes
	def developMap(self):
	
		# start the free search going down	
		self.metaPath = [(self.nodeList[0].type, self.nodeList[0].edge.relationship, 'down', \
							self.landmarks[0][3], 'node')]
	
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
		
			map.append((sNode.type, sNode.edge.relationship, direction, self.landmarks[self.nodeList.index(sNode)][3], 'node'))
			
			self.minPathLength = len(map)
			self.minPath = map
			return
			
		# another ending condition
		elif len(map) >= self.minPathLength or len(sNode.children) == 0 or sNode.value == 'root':
			# need to quite the search
			return
			
		elif direction == 'down':
		
			# we still need to append the relationship
			map.append((sNode.type, sNode.edge.relationship, direction, 'null'))
			
			# we can afford to do a breath-first search
			for child in sNode.children:
				self.findShortestPath(child, tNode, copy(map), 'down')
			
		elif direction == 'up':
		
			# we still need to append the relationship
			map.append((sNode.type, sNode.edge.relationship, direction, 'null'))
			
			# we can afford to do a breath-first search
			for child in sNode.children:
				self.findShortestPath(child, tNode, copy(map), 'down')
				
			self.findShortestPath(sNode.parent, tNode, copy(map), 'up')
			
		else:
			print 'we are in big trouble!913'
	
