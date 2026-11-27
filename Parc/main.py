# main.py
from flask import Flask
from model import Model
from controller import register_routes

app = Flask(__name__)
model = Model()
register_routes(app, model)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)