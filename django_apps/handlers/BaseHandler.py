class BaseHandler(object):
	
	def __init__(self):
		self.__results = []
	
	def __save(self, name, data, description, group):
		dataDict = {
				'name' : name,
				'data' : data,
				'description' : description,
				'group' : group,
					}
		return dataDict
	
	def saveInt(self,name,data,description="",group=""):
		if name == '' or data == '':
			return False
		
		dataDict = self.__save(name, data, description, group)
		dataDict['type'] = 'Integer'
		
		self.__results.append(dataDict)
	
	def saveFloat(self,name,data,description="",group=""):
		if name == '' or data == '':
			return False
		
		dataDict = self.__save(name, data, description, group)
		dataDict['type'] = 'Float'
		
		self.__results.append(dataDict)
	
	def saveBinary(self,name,data,ROOT_version,description="",group=""):
		if name == '' or data == '' or ROOT_version == '':
			return False
		
		dataDict = self.__save(name, data, description, group)
		dataDict['type'] = 'Float'
		dataDict['ROOT_version'] = ROOT_version
		
		self.__results.append(dataDict)
	
	def saveString(self,name,data,description="",group=""):
		if name == '' or data == '':
			return False
		
		dataDict = self.__save(name, data, description, group)
		dataDict['type'] = 'String'
		
		self.__results.append(dataDict)
		
	def getResults(self):
		return self.__results
	
	def collectResults(self, directory='.'):
		return NotImplementedError()
		
		
	
	 