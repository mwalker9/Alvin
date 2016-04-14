# a node
import Edge

class Node(object):

	def __init__(self, value, type, parent, relationship):
		self.value = value
		self.type = type
		self.children = []
		self.parent = parent
		self.edge = Edge.Edge(relationship)
		self.checked = False
		
	def acceptRule(self, rules):
	
		l = []
		
		idx = 0
		for child in self.children:
			if child.edge.relationship == rules[idx]:
				l.append(child.value)
				idx += 1
				
		return l