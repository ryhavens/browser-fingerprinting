from flask import Flask, request
app = Flask(__name__, static_url_path='/', static_folder='')

@app.route('/', methods=['GET'])
def index():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)