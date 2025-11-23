from flask import Flask

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "OK - app.py importou e a rota / respondeu"