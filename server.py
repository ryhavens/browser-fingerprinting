from flask import Flask, request, send_from_directory
# from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.pymongo import PyMongo, MongoClient

import json
import pprint
import os
import datetime

app = Flask(__name__, static_url_path='/', static_folder='')

mongo_uri = os.environ['MONGODB_URI'] or None
mongo = None

# if we are running in a heroku environment, or have a shared db, connect to that
if (mongo_uri): 
    mongo = MongoClient(mongo_uri)
# else try to connect to local mongo instance
else: 
    mongo = PyMongo(app)

@app.route('/', methods=['GET'])
def index():
    return app.send_static_file('index.html')

@app.route('/js/<path:path>', methods=['GET'])
def send_js(path):
    return send_from_directory('js',path)

@app.route('/store_fingerprint', methods=['POST'])
def store_fingerprint():
    content = request.get_json(silent=True, force=True)
    fingerprint = content['fingerprint']
    user = mongo.db.users.find({'fingerprint':fingerprint})
    n_records = user.count()
    print n_records
    if n_records:
        if (n_records > 1):
            print 'Multiple users with this fingerprint %s' % fingerprint
        else:
            print 'Found matching fingerprint for this user %s' % fingerprint
    else:
        print 'New fingerprint %s' % fingerprint

        to_insert = {
                'fingerprint':fingerprint,
                'components':json.dumps(content['components']),
                'created_at':datetime.datetime.utcnow(),
                'updated_at':datetime.datetime.utcnow()
        }

        returned_id = mongo.db.users.insert_one(to_insert)

    # print content


    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)