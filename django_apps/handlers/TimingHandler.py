import os
from BaseHandler import BaseHandler
from xml.etree.ElementTree import ElementTree
from xml.parsers.expat import ExpatError

class TimingHandler(BaseHandler):
	
	def __init__(self):
		super(self.__class__, self).__init__()

	def collectResults(self,directory):
		try:
			os.chdir(directory)
		except OSError:
			return False
		
		tree = ElementTree()
		
		try:
			tree.parse('timing.xml')
		except ExpatError:
			return False
		except IOError:
			return False
		
		for parent in tree.getiterator('alg'):
			for child in parent:
				if child.tag == 'count':
					self.saveInt(parent.attrib.get("name")+'_'+child.tag, child.text)
				else:
					self.saveFloat(parent.attrib.get("name")+'_'+child.tag, child.text)