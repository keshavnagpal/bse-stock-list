from flask import Flask, flash, redirect, render_template, g, Response, request, session, abort, jsonify
import json
from flask_cors import CORS
import helpers as HM
from flask_caching import Cache
from flask_compress import Compress

cachetime = 100
app = Flask(__name__)
#This is for the app cache, not the bse data cache in redis
cache = Cache(app, config={"CACHE_TYPE": "simple"})
Compress(app)

# To accept requests from any domain / IP
CORS(app)

@app.route('/')
def hello_world():
	return 'You are a curious fellow!'

# since the files get updated everyday, this could be moved to a scheduled webjob
@cache.memoize(timeout=10000)
@app.route('/bse')
def bse():
	# DownloadAndSaveBSEToRedis()
	BSEFile = HM.DownloadBSEFile()
	stockdf = HM.extractZipFile(BSEFile)
	HM.saveFieldsToRedis(stockdf)
	return render_template('bse.html')

@app.route("/getBSEData", methods=['GET'])
def getBSEData():		
	return HM.getFieldsFromRedis()

 
if __name__ == '__main__':
	app.run(debug=True)
