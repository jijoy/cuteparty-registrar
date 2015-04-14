import os
import json
from threading import Thread
import time
from time import sleep
from flask import Flask, json, render_template, request
import redis
from collections import OrderedDict

from Queue import Queue

app = Flask(__name__)
port = int(os.getenv("PORT"))
vcap = json.loads(os.environ['VCAP_SERVICES'])
svc = vcap['rediscloud'][0]['credentials']

db = redis.StrictRedis(host=svc["hostname"], port=svc["port"], password=svc["password"],db=0)


@app.route('/update',methods=['POST'])
def update():
    """
    This is the entry point for updating the aggregator info
    Each of the invidividual apps will call this endpoint with their latest info
    """
    appname = request.form['applicationname']
    appdetails = request.form['appinfo']
    obj = json.loads(appdetails)
    if appname and obj:
        db.hset('applications', appname, appdetails)
    return json.dumps({'message':'success'})



@app.route('/applicationsdetails')
def applicationsdetails():
    """
    This is the endpoint for providing all info about the applications 
    This is an internal method for registrator through which index.html loads all info
    """
    appdicts = db.hgetall('applications')
    finaldict = OrderedDict()
    for appname in sorted(appdicts):
        instances = json.loads(appdicts.get(appname))
        finaldict.__setitem__(appname,instances)
    return render_template('robots.html', appdicts=finaldict)


@app.route('/')
def index():
    """
    Main entry point
    """
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=port, debug=True)
