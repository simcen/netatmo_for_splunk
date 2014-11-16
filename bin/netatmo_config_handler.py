import splunk.admin as admin
import splunk.entity as en


class ConfigApp(admin.MConfigHandler):

	def setup(self):
		if self.requestedAction == admin.ACTION_EDIT:
			for arg in ['client-id', 'client-secret']:
				self.supportedArgs.addOptArg(arg)
				
	def handleList(self, confInfo):
		confDict = self.readConf("netatmo")
		if None != confDict:
			for stanza, settings in confDict.items():
				for key, val in settings.items():
					if key in ['client-id', 'client-secret', 'base', 'authorization', 'getuser', 'devicelist', 'getmeasure'] and val in [None, '']:
						val = ''
					confInfo[stanza].append(key, val)
					

	def handleEdit(self, confInfo):
		name = self.callerArgs.id
		args = self.callerArgs
		
		if self.callerArgs.data['client-id'][0] in [None, '']:
			self.callerArgs.data['client-id'][0] = ''
		
		if self.callerArgs.data['client-secret'][0] in [None, '']:
			self.callerArgs.data['client-secret'][0] = ''	
				
		self.writeConf('netatmo', 'auth', self.callerArgs.data)
			
# initialize the handler
admin.init(ConfigApp, admin.CONTEXT_NONE)