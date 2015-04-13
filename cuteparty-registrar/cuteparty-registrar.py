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
    appname = request.form['applicationname']
    appdetails = request.form['appinfo']
    print appdetails
    if appname and appdetails:
        db.hset('applications', appname, appdetails)
    return json.dumps({'message':'success'})



@app.route('/applicationsdetails')
def applicationsdetails():
    appdicts = db.hgetall('applications')
    finaldict = OrderedDict()
    print appdicts
    for appname in sorted(appdicts):
        finaldict.__setitem__(appname,db.hgetall(appname))
#     print mydict
    mylist = []
    return render_template('robots.html', appdicts=finaldict)


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=port, debug=True)
