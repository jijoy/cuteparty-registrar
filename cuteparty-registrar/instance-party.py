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

application_name = json.loads(os.environ['VCAP_APPLICATION'])['application_name']

class Producer(Thread):
    def __init__(self,queue):
        Thread.__init__(self)
        self.queue = queue 
    def run(self):
        while True :
            try:
                instance_id = os.getenv("CF_INSTANCE_INDEX")
                mydict = db.hgetall(application_name)
                if instance_id not in mydict :
                    self.queue.put(instance_id)
            except :
                pass
            finally:
                pass
class Consumer(Thread):
    def __init__(self,queue):
        Thread.__init__(self)
        self.queue = queue
    
    def run(self):
        while True :
            try :
                instance_id = self.queue.get()
                db.hset(application_name,instance_id,1)
            except:
                pass
            finally:
                pass
        
def init_workers():
    party_queue = Queue()
    p = Producer(party_queue)
    p.daemon = True
    c = Consumer(party_queue)
    c.deamon= True
    p.start()
    c.start()

@app.route('/addthread')
def addthread():
    instance_id = os.getenv("CF_INSTANCE_INDEX")
    print 'Instance Id ****************%s'%instance_id
    thread_count = int(db.hget(application_name,instance_id))
    thread_count+=1
    print 'Threadcount ****************%s'%thread_count
    result = db.hset(application_name,str(instance_id),str(thread_count))
    print 'HSET result %s'%result
    print db.hgetall(application_name)
    return json.dumps({'message':'success'})
@app.route('/deletethread')
def deletethread():
    instance_id = os.getenv("CF_INSTANCE_INDEX") 
    print 'Instance Id **************%s'%instance_id
    thread_count = int(db.hget(application_name,instance_id))
    thread_count-=1
    db.hset(application_name,instance_id,thread_count)
    
    return json.dumps({'message':'success'})

@app.route('/register')
def register():
    db.hset('applications',application_name,1)
#     print mydict
    return json.dumps({'message':'success'})


@app.route('/instances')
def instances():
    mydict = db.hgetall(application_name)
    ordered = OrderedDict()
    for key in sorted(mydict):
        ordered.__setitem__(key,mydict.get(key))
#     print mydict
    mylist = []
    return render_template('robots.html', mydict=ordered)

@app.route('/applications')
def applications():
    return render_template('applications.html')

@app.route('/applicationsdetails')
def applicationsdetails():
    appdicts = db.hgetall('applications')
    finaldict = OrderedDict()
    for appname in sorted(appdicts):
        finaldict.__setitem__(appname,db.hgetall(appname))
#     print mydict
    mylist = []
    return render_template('app-robots.html', appdicts=finaldict)


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    init_workers()
    app.run(host='0.0.0.0', port=port, debug=True)
