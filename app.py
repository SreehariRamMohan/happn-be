
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from flask_pymongo import PyMongo, ObjectId
from flask_socketio import SocketIO, emit
from flask_bcrypt import Bcrypt
#  from flask_jwt_extended import JWTManager, jwt_required, create_access_token, create_refresh_token, get_jwt_identity
#  , jwt_refresh_token_required

import requests
import os
import json
import uuid

PORT = "5000"
app = Flask(__name__)
cors = CORS(app)
socketio = SocketIO(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SECRET_KEY'] = os.environ.get("HAPPEN_SECRET_KEY")

# JWT Manager
#  jwt = JWTManager(app)

# bcrypt
bcrypt = Bcrypt(app)

# MongoDB
connectionString = "mongodb+srv://hackPrinceton:" + str(os.environ.get("HAPPEN_MONGO_PASSWORD")) + "@cluster0.gor2j.mongodb.net/happen?retryWrites=true&w=majority"
app.config["MONGO_URI"] = connectionString
mongo = PyMongo(app)
db = mongo.db


@app.route("/signup", methods=["POST"])
def signup(): 
    print("in signup")
    username = request.json["username"]
    password = request.json["password"]


    same_username_users = db.users.find( {"username": username } ) 
    if any(True for _ in same_username_users):
        return jsonify({ "status": "error", "messsage": "username taken" }), 409

    pw_hash = bcrypt.generate_password_hash(password)
    friend_code = str(uuid.uuid4())
    mongo_id = db.users.insert_one({ "username": username, "password": pw_hash, "friend_code": friend_code }).inserted_id

    print(mongo_id)

    #  access_token = create_access_token(identity=username, expires_delta=False)

    return_json = {"status": "success", 'mongo_id': mongo_id}
    return json.dumps(return_json, default=str), 200

@app.route("/login", methods=["POST"])
def login(): 
    username = request.json["username"]
    password = request.json["password"]

    mongo_user = mongo.db.users.find_one({"username": username})
    pw_hash = mongo_user["password"]

    if bcrypt.check_password_hash(pw_hash, password):

        #  access_token = create_access_token(identity=username, expires_delta=False)
        print(json.dumps(mongo_user["_id"], default=str))
        return_json = {"status": "success", 'mongo_id': mongo_user["_id"]}
        return json.dumps(return_json, default=str), 200
    else: 
        return jsonify({"status": "error", "message": "incorrect username or password"}), 401

#  @jwt_required
@app.route('/uploadFormData', methods=["POST"])
def uploadFormData(): 
    mongo_id = request.json["mongo_id"]
    fa1 = request.json["fq1"]
    fa2 = request.json["fq2"]
    fa3 = request.json["fq3"]
    fa4 = request.json["fq4"]
    fa5 = request.json["fq5"]

    formAnswers = {
        "formAnswer1": fa1, 
        "formAnswer2": fa2, 
        "formAnswer3": fa3, 
        "formAnswer4": fa4, 
        "formAnswer5": fa5 
    }

    mongo_user = mongo.db.users.find_one({"_id": ObjectId(mongo_id)})
    friend_code = mongo_user["friend_code"]

    db.users.find_one_and_update({'_id': ObjectId(mongo_id)}, { "$set": {"formAnswers": formAnswers }})
    res = requests.post("http://34.121.220.212:5000/", json={ 'fa1': fa1, 'fa2': fa2, 'fa3': fa3, 'fa4': fa4, 'fa5': fa5, 'friend_code': friend_code })

    return jsonify({"status": "success"}), 200

#  @jwt_required
@app.route('/updateBio', methods=["POST"])
def updateBio(): 
    mongo_id = request.json["mongo_id"]
    description = request.json["description"]
    blurb1 = request.json["blurb1"]
    blurb2 = request.json["blurb2"]
    blurb3 = request.json["blurb3"]

    bio = {
        "description": description, 
        "blurb1": blurb1, 
        "blurb2": blurb2, 
        "blurb3": blurb3 
    }

    #  mongo_user = mongo.db.users.find_one({"username": username})

    print("before update")
    db.users.find_one_and_update({'_id': ObjectId(mongo_id)}, { "$set": {"bio": bio }})
    print("after update")

    #  mongo_user.formAnswers.insert_one(formAnswers)
    #  db.users.formAnswers.insert_one(formAnswers)
    return jsonify({"status": "success"}), 200

@socketio.event
def my_event(message):
    emit('my response', {'data': 'got it!'})


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)

