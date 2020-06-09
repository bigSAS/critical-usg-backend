from flask import Flask
app = Flask(__name__)


@app.route('/', methods=("POST",))
def hello_world():
    """ Hello world - flask app"""
    return {
        "hello": "world - app is live and running :)"
    }
