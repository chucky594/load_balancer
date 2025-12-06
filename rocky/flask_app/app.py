from flask import Flask
import socket
app = Flask(__name__)

@app.route('/')
def index():
    return f"<h1>Jovadrops — Flask on {socket.gethostname()}</h1>"

@app.route('/health')
def health():
    return "OK", 200

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
