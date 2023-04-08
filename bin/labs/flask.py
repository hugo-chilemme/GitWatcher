from flask import Flask
app = Flask(__name__)

last_commit = {}

@app.route("/api/endpoint2/commits")
def hello_world():
    return last_commit

def set_last_commit(commit):
    last_commit = commit
    
    
def start_flask():
    print('Flask started')
    app.run(host='0.0.0.0', port=8888)
