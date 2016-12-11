from flask import Flask, request, send_from_directory
import json
import pprint

app = Flask(__name__, static_url_path='/', static_folder='')

@app.route('/', methods=['GET'])
def index():
    return app.send_static_file('index.html')

@app.route('/js/<path:path>', methods=['GET'])
def send_js(path):
    return send_from_directory('js',path)

@app.route('/store_fingerprint', methods=['POST'])
def store_fingerprint():
    content = request.get_json(silent=True, force=True)
    print content
    print json.loads(request.data)
    print pprint.pformat(request.environ, depth=5)
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)