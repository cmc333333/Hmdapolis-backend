from flask import Flask, request
import json

app = Flask(__name__)

@app.route("/")
def hello():
    data = {'response': [
        {'name': 'accepted', 'count': 8},
        {'name': 'rejected', 'count': 4},
        ]}
    if request.args.getlist("callback"):
        callback = request.args.getlist("callback")[0]
        return callback + '(' + json.dumps(data) + ');'
    return json.dumps(data)

@app.route("/dev/")
def dev():
    return "herro?"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8180, debug=True)
