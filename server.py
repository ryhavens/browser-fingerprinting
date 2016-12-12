from flask import Flask, request, send_from_directory, make_response
from flask.ext.pymongo import PyMongo, MongoClient
from bson.objectid import ObjectId # solve bug: string ID =/= object ID
from bson import json_util

import sys
import json
import pprint
import os
import datetime

app = Flask(__name__, static_url_path='/', static_folder='')

mongo_uri = os.getenv('MONGODB_URI')
db_name = os.getenv('MONGODB_NAME')
db = None

# if we are running in a heroku environment, or have a shared db, connect to that
if (mongo_uri): 
    with app.app_context():
        assert db_name is not None # I'll eat a sock if this throws an error
        db = MongoClient(mongo_uri)[db_name]
# else try to connect to local mongo instance
else: 
    with app.app_context():
        db = PyMongo(app).db

@app.route('/', methods=['GET'])
def index():
    sys.stdout.flush() # debugging heroku issue where stdout is buffered
    return app.send_static_file('index.html')

@app.route('/js/<path:path>', methods=['GET'])
def send_js(path):
    return send_from_directory('js',path)

@app.route('/store_fingerprint', methods=['POST'])
def store_fingerprint():
    user_id = request.cookies.get('uid')
    if (user_id): # ObjectId of None gets converted into an actual ID... lol
        try:
            user_id = ObjectId(user_id) # convert uid to objectid
        except:
            user_id = None

    content = request.get_json(silent=True, force=True)

    # required fields
    if ('fingerprint' not in content or 'components' not in content or 'action' not in content):
        return json.dumps({'error':True}), 400, {'ContentType':'application/json'}

    fingerprint = content['fingerprint']

    user_cursor = None
    # user has been assigned a tracking cookie so we can trace changes
    # in their fingerprint

    if (user_id):
        user_cursor = db.users.find({'_id': user_id})
        if user_cursor.count() == 0:
            # user entry is bad, this is an attempt at hijacking the cookie
            return json.dumps({'error':True, 'id':str(user_id)}), 400, {'ContentType':'application/json'}
        else:
            # found a user
            user_entry = user_cursor[0]
            # track fingerprint changes
            if (user_cursor[0]['fingerprint'] != fingerprint):
                log_activity(user_id, 'Fingerprint changed from ' + user_cursor[0]['fingerprint'] + ' to ' + fingerprint)
                change_fingerprint(user_id, 
                    fingerprint, json.dumps(content['components']), 
                    user_cursor[0]['fingerprint'], user_cursor[0]['components'])

            if (content['action'] == 'check'):
                log_activity(user_id, 'Visited the page again')
            elif (content['action'] == 'activity'):
                log_activity(user_id, content['activity'])

            return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

    user_cursor = db.users.find({'fingerprint':fingerprint})
    n_records = user_cursor.count()

    if n_records:
        if (n_records > 1):
            print 'Multiple users with this fingerprint %s' % fingerprint
            # no idea how to handle this yet, so return "Not Implemented"
            return json.dumps({'success':False,'error':False}), 501, {'ContentType':'application/json'}
        else:
            # user is trying to dodge system by deleting their cookie, but we
            # found them! (or it could be a different user with the same fingerprint
            # but we will ignore that for now)
            user_id = user_cursor[0]['_id'] # reset user id to make new cookie
            log_activity(user_id, 'Tried to dodge tracking by unsetting cookie')

            if (content['action'] == 'check'):
                log_activity(user_id, 'Visited the page again')
            elif (content['action'] == 'activity'):
                log_activity(user_id, content['activity'])

            print 'Found matching fingerprint for this user %s' % fingerprint
    else:
        print 'New fingerprint %s' % fingerprint

        to_insert = {
                # id is implicit, assuming unique fingerprints for everyone
                'fingerprint':fingerprint,
                'components':json.dumps(content['components']),
                'activity_log':[{
                    'activity': 'First encounter', 
                    'time': datetime.datetime.utcnow()
                    }],
                'old_fingerprints': [],
                'created_at':datetime.datetime.utcnow(),
                'updated_at':datetime.datetime.utcnow()
        }

        user_id = db.users.insert(to_insert)

    print user_id
    resp = make_response(json.dumps({'success':True}), 200, {'ContentType':'application/json'})
    resp.set_cookie('uid', str(user_id))
    return resp

@app.route('/view_fingerprint/<fingerprint>', methods=['GET'])
def view_fingerprint_data(fingerprint):
    user_id = request.cookies.get('uid')
    if (user_id): # ObjectId of None gets converted into an actual ID... lol
        try:
            user_id = ObjectId(user_id) # convert uid to objectid
        except:
            user_id = None

    user = db.users.find({'fingerprint':fingerprint})

    if user_id:
        viewing_user = db.users.find({'_id': user_id})
        if viewing_user.count():
            log_activity(user_id, 'Viewed fingerprint data for ' + fingerprint)
            

    if user.count():
        # assuming no multiples
        # http://stackoverflow.com/questions/11875770/how-to-overcome-datetime-datetime-not-json-serializable-in-python
        resp = make_response(json.dumps(user[0], default=json_util.default), 200, {'ContentType':'application/json'})
    else:
        resp = make_response(json.dumps({'error':'Not found'}), 404, {'ContentType':'application/json'})

    return resp

def log_activity(user_id, activity):
    db.users.update(
        {'_id': user_id},
        {'$set': {
            'updated_at':datetime.datetime.utcnow()
            },
        '$addToSet': {
            'activity_log': {
                'activity': activity,
                'time': datetime.datetime.utcnow()
                }
            }
        })

def change_fingerprint(user_id, fingerprint, components, old_fingerprint, old_components):
    db.users.update(
        {'_id': user_id},
        {'$set': {
            'fingerprint': fingerprint,
            'components': components
            },
        '$addToSet': {
            'old_fingerprints': {
                'fingerprint': old_fingerprint,
                'components': old_components,
                'changed_at': datetime.datetime.utcnow()
                }
            }
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)