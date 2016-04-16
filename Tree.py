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
		self.foundNodes = []
		self.xcompD = {}
		self.dobjList = []
		self.termD = {}
		self.termDPath = '.\InspirationSet\\termD.txt'
		self.rules = []
		
		
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

	def findNode(self, Node, dataTup):
		
		if Node.type == dataTup[0] and Node.edge.relationship == dataTup[1]:
		
			self.foundNodes.append(Node)
				
		else:
			for child in Node.children:			
				self.findNode(child, dataTup)
					
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

			
	def parseFunctions(self, Node, funcList, termList):
	
		#try:
		
		if len(funcList) == 0:
			self.termListToRule(termList)
			#print termList
			#print 'this is the end of the road, folks!'
			
		elif Node.type == funcList[0][0] and Node.edge.relationship == funcList[0][1]:
			if len(funcList[0]) == 5:
				#print 'here',funcList[0], Node.value
				termList.append((Node.value, funcList[0][3]))
				
			if len(funcList) == 1:	
				self.parseFunctions(Node, deepcopy(funcList[1:]), deepcopy(termList))	
			
			elif funcList[1][2] == 'down':
				for child in Node.children:
					#print child.value, 'child of', Node.value
					self.parseFunctions(child, deepcopy(funcList[1:]), deepcopy(termList))
					
			elif funcList[1][2] == 'up':
				self.parseFunctions(Node.parent, deepcopy(funcList[1:]), deepcopy(termList))
				
			else:
				print 'we are in trouble139'
		
	def termListToRule(self, termList):
		
		#termList.reverse()
		#print termList
		
		l = ['(', ',', ')']
		
		for i, tup in enumerate(termList):
		
			if tup[1] == 'variable':
				
				if i == 0:
					l.insert(l.index(')'), str(tup[0]))
				else:
					l.insert(l.index('(') + 1, str(tup[0]))
				
			elif tup[1] == 'function':
				l.insert(0, '&' + str(tup[0]))
				
			else:
				print tup
				print 'we are in trouble153!'
				
		s = str(l).replace('[','').replace(']','').replace(', ', '').replace("'", "")
		self.rules.append(s[1:])
			
		
		
		
		
