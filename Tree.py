# a tree
from copy import deepcopy
import Node
reload(Node)
import cPickle

class Tree(object):
	
	def __init__(self, root, dependencies, idx):
		self.rootValue = root
		self.rootIdx = idx
		self.dependencies = dependencies
		self.usedIndices = set([])
		self.root = ''
		self.foundNode = None
		self.xcompD = {}
		self.dobjList = []
		self.termD = {}
		self.termDPath = '.\InspirationSet\\termD.txt'
		self.rule = ''
		
		
	def createHead(self, node):
				
		# build all dependencies
		for i, (g, r, d) in enumerate(self.dependencies):
		
			# this means there is a dependent with a similar word
			if node.value == d[0] and node.parent.value != g[0] and i not in self.usedIndices:
				break
				
			elif node.value == d[0] and node.parent.value != g[0]:
				# we can just pass
				continue
			
			# find all the relationships that have the head as a governor
			elif g[0] == node.value and i not in self.usedIndices:
				newNode = Node.Node(d[0], d[1], node, r)
				self.usedIndices.add(i)
				#print 'created', d[0], d[1], 'from', g[0]
				node.children.append(newNode)
				self.createHead(newNode)
				
	def findNodeWrapper(self, value, type, parent, relationship, function):
		
		# finds children
		# another variation is to find parent
		
		# nullify the foundNode variable
		self.foundNode = None
		
		if function == 'substructures':
			self.findNodeSubstructures(self.root, value, type, parent, relationship)
		else:
			self.findNodeBuildTree(self.root, value, type)

	def findNodeSubstructures(self, Node, value, type, parent, relationship):
		
		if Node.value == value and Node.type == type and Node.parent == parent and Node.edge.relationship == relationship:
		
			self.foundNode = Node
				
		else:
			for child in Node.children:			
				try:
					self.findNodeSubstructures(child, value, type, parent, relationship)
					
				except:
					print 'something went wrong'
					pass	
					# this means that there is no need to keep progressing down this branch
					
	def findNodeBuildTree(self, Node, value, type):
		
		if Node.value == value and Node.type == type:			
			if Node.checked == False:
				self.foundNode = Node
				Node.checked = True
				
		else:
			for child in Node.children:			
				try:
					self.findNodeBuildTree(child, value, type)
					
				except:
					print 'something went wrong'
					pass	
					# this means that there is no need to keep progressing down this branch
			
	def addNode(self, value, type, parent):
		pass
		
	def toString(self, node):
		print node.value
		for child in node.children:
			print '('
			self.toString(child)
		print ')'
		
	def buildTree(self):
	
		# build root
		g, r, d = self.dependencies[self.rootIdx]
		
		# root Node
		node = Node.Node('root', 'root', 'root', 'root')
		
		self.root = Node.Node(g[0], g[1], node, 'root')
		node.children.append(self.root)
		self.createHead(self.root)
		
	def findRelationship(self, Node, funcList, term, direction, termList):
	
		#print Node.value, Node.edge.relationship, len(Node.children), direction
		
		if Node.edge.relationship == term:	

			if len(funcList[0]) == 3:
				# we have hit a node
				termList.append((Node.value, 'relationship'))
			#print term, Node.value			
			self.parseFunctions(Node, deepcopy(funcList[1:]), deepcopy(termList))
			
		elif direction == 'down':
			for child in Node.children:
				#print child.value, 'child of', Node.value
				self.findRelationship(child, deepcopy(funcList), term, direction, deepcopy(termList))
				
		elif direction == 'up':
			self.findRelationship(Node.parent, deepcopy(funcList), term, direction, deepcopy(termList))
			
		else:
			print 'we are in trouble'
			
	def findType(self, Node, funcList, term, direction, termList):
			
		#		case of verbs      case of nouns	
		if Node.type[0] == term or Node.type == term:
			if len(funcList[0]) == 3:
				# we have hit a node
				termList.append((Node.value, 'type'))
			#print term, Node.value			
			self.parseFunctions(Node, deepcopy(funcList[1:]), deepcopy(termList))
		
		elif direction == 'down':
			for child in Node.children:
				self.findType(child, deepcopy(funcList), term, direction, deepcopy(termList))
				
		elif direction == 'up':
			self.findType(Node.parent, deepcopy(funcList), term, direction, deepcopy(termList))
			
		else:
			print 'we are in trouble'
			
	def parseFunctions(self, Node, funcList, termList):
	
		#try:
		
		if len(funcList) == 0:
			self.termListToRule(termList)
			#print termList
			#print 'this is the end of the road, folks!'
			
		elif self.termD[funcList[0][0]] == 'relationship':
			#print funcList[0]
			#									  relationship	  direction
			self.findRelationship(Node, deepcopy(funcList), funcList[0][0], funcList[0][1], deepcopy(termList))
			
		elif self.termD[funcList[0][0]] == 'type':
			#print funcList[0]
			#							  type			  direction
			self.findType(Node, deepcopy(funcList), funcList[0][0], funcList[0][1], deepcopy(termList))
				
		#except:
		#	print 'broke chain at', Node.value, 'looking for', funcList[0]
			
	def loadTermD(self):
		
		f = open(self.termDPath, 'r')
		self.termD = cPickle.load(f)
		f.close()
		
	def termListToRule(self, termList):
		
		#termList.reverse()
		
		l = ['(', ',', ')']
		
		for i, tup in enumerate(termList):
		
			if tup[1] == 'relationship':
				
				if i == 0:
					l.insert(l.index(')'), str(tup[0]))
				else:
					l.insert(l.index('(') + 1, str(tup[0]))
				
			elif tup[1] == 'type':
				l.insert(0, '&' + str(tup[0]))
				
			else:
				print 'we are in real trouble!'
				
		s = str(l).replace('[','').replace(']','').replace(', ', '').replace("'", "")
		self.rule = s[1:]
			
		
		
		
		
