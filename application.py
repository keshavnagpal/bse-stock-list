import cherrypy
import json
import helpers as HM
import os

class Root(object):
	@cherrypy.expose
	def index(self):		
		return "You're a curious fellow!"

	@cherrypy.expose
	def bse(self):
		BSEFile = HM.DownloadBSEFile()
		stockdf = HM.extractZipFile(BSEFile)
		HM.saveFieldsToRedis(stockdf)
		return open("templates/bse.html")

	@cherrypy.expose
	@cherrypy.tools.response_headers(headers=[('Content-Type', 'application/json')])
	def getBSEData(self):		
		return HM.getFieldsFromRedis()


CP_CONF = {
	'/media': {
		'tools.staticdir.on': True,
		'tools.staticdir.dir': os.path.abspath('./') # staticdir needs an absolute path
		}
	}
app = cherrypy.Application(Root(),'/', CP_CONF)

if __name__ == '__main__':
	from wsgiref.simple_server import make_server

	httpd = make_server('', 5000, app)
	httpd.serve_forever()