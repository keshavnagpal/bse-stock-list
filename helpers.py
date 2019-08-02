import json
import datetime as dt
import redis
import httplib2
from io import BytesIO
from zipfile import ZipFile
import pandas as pd

r = redis.StrictRedis(host='sdztest.redis.cache.windows.net',
        port=6380, db=0, password='4vjBFdTGgyiiefz4fvUZRqQ65L5wNFmnHxowVRylBKc=', ssl=True)

def DownloadBSEFile():	
	URL = 'https://www.bseindia.com/download/BhavCopy/Equity/'

	today = dt.datetime.today()

	i=1
	while(True):
		
		day = today.day
		if(day<10):
			day = '0'+str(day)
		month = today.month
		if(month<10):
			month = '0'+str(month)
		year = today.year

		fileName = 'EQ'+str(day)+str(month)+str(year)[2:4]+'_CSV.ZIP'
		FileURL = URL + fileName
		h = httplib2.Http(".cache")
		resp, content = h.request(FileURL, "GET")
		if(resp['status']!='404'):
			r.set("FileDate", today.strftime('%d %b %Y'))
			break
		today = today - dt.timedelta(i)
	return content

def extractZipFile(resp):
	zipfile = ZipFile(BytesIO(resp))
	#print(zipfile.namelist())
	zipfile.extract(zipfile.namelist()[0])
	stockdf = pd.read_csv(zipfile.namelist()[0])
	return stockdf

def saveFieldsToRedisOld(stockdf):
	stockCode = list(stockdf.SC_CODE)
	stockName = list(stockdf.SC_CODE)
	stockHigh = list(stockdf.HIGH)
	stockLow = list(stockdf.LOW)
	stockOpen = list(stockdf.OPEN)
	stockClose = list(stockdf.CLOSE)
	stockDiffFromPrevClose = list((stockdf.CLOSE - stockdf.PREVCLOSE)/stockdf.CLOSE)
	print(stockDiffFromPrevClose)
	stockDict = {
		'code':stockCode,
		'name':stockName,
		'high':stockHigh,
		'low':stockLow,
		'open':stockOpen,
		'close':stockClose,
		'change':stockDiffFromPrevClose,
		'FileDate': r.get('FileDate').decode()
		}
	stockJson = json.dumps(stockDict)
	r.set("stockJson",stockJson)

def saveFieldsToRedis(stockdf):
	final_stocks = stockdf[['SC_CODE','SC_NAME','HIGH','LOW','OPEN','CLOSE']]
	final_stocks['change'] = ((stockdf.CLOSE - stockdf.PREVCLOSE)/stockdf.CLOSE) * 100
	stockDict = final_stocks.to_dict('records')
	stockDict[0]['FileDate'] = r.get('FileDate').decode()	
	print(final_stocks)
	stockJson = json.dumps(stockDict)
	r.set("stockJson",stockJson)

def getFieldsFromRedis():	
	stockJson = r.get("stockJson")
	return stockJson
