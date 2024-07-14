from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from src.utils import print_ascii_art

app = Flask(__name__)
CORS(app)

client = MongoClient('localhost', 27017)
db = client['forex']

@app.route("/api/strengths/max_daily", methods=["GET"])
def get_max_daily_strengths():
    collection = db['relative_strengths']
    strengths = list(collection.find({}, {'_id': False}))
    return jsonify(strengths)

if __name__ == "__main__":
    print_ascii_art()
    app.run(debug=True)
