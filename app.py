
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

cors = CORS(app, resources={r"/*":{"origins": "*", "supports_credentials": True}})
socketio = SocketIO(app, cors_allowed_origins="*")
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SECRET_KEY'] = os.environ.get("HAPPEN_SECRET_KEY")
ML_SERVER_URL = str(os.environ.get("HAPPEN_ML_SERVER_URL"))

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

    return_json = {"status": "success", 'mongo_id': mongo_id}
    return json.dumps(return_json, default=str), 200

@app.route("/login", methods=["POST"])
def login(): 
    username = request.json["username"]
    password = request.json["password"]

    mongo_user = mongo.db.users.find_one({"username": username})
    pw_hash = mongo_user["password"]
    friend_code = mongo_user["friend_code"]

    if bcrypt.check_password_hash(pw_hash, password):

        print(json.dumps(mongo_user["_id"], default=str))
        return_json = {"status": "success", 'mongo_id': mongo_user["_id"], 'friend_code': friend_code }
        return json.dumps(return_json, default=str), 200
    else: 
        return jsonify({"status": "error", "message": "incorrect username or password"}), 401

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
    res = requests.post(ML_SERVER_URL + "questions", json={ 'fa1': fa1, 'fa2': fa2, 'fa3': fa3, 'fa4': fa4, 'fa5': fa5, 'friend_code': friend_code })

    matchesRes = requests.post(ML_SERVER_URL + "matches", json={'friend_code': friend_code })
    matchData = matchesRes.json()

    potential_friend_code = matchData["uid"]
    db.users.find_one_and_update({'_id': ObjectId(mongo_id)}, { "$push": {"friends": potential_friend_code }})

    print("match data: ")
    print(matchData)

    return jsonify({"status": "success", "matchData": matchData}), 200

@app.route('/updateBio', methods=["POST"])
def updateBio(): 
    mongo_id = request.json["mongo_id"]
    blurb1 = request.json["blurb1"]
    blurb2 = request.json["blurb2"]
    blurb3 = request.json["blurb3"]
    blurb4 = request.json["blurb4"]

    bio = {
        "blurb1": blurb1, 
        "blurb2": blurb2, 
        "blurb3": blurb3 
        "blurb4": blurb4 
    }

    #  mongo_user = mongo.db.users.find_one({"username": username})

    print("before update")
    db.users.find_one_and_update({'_id': ObjectId(mongo_id)}, { "$set": {"bio": bio }})
    print("after update")

    #  mongo_user.formAnswers.insert_one(formAnswers)
    #  db.users.formAnswers.insert_one(formAnswers)
    return jsonify({"status": "success"}), 200

@app.route('/getUserInfo', methods=["POST"])
def getUserInfo(): 
    mongo_id = request.json["mongo_id"]
    mongo_user = mongo.db.users.find_one({"username": username})
    friend_data = mongo_user["friend"]
    bio = mongo_user["bio"]
    formData = mongo_user["formData"]
    return jsonify({"status": "success", "friends": friend_data, "formData": formData, "bio": bio}), 200

@app.route('/getFriends', methods=["POST"])
def getFriends(): 
    mongo_id = request.json["mongo_id"]
    mongo_user = mongo.db.users.find_one({"username": username})
    friend_data = mongo_user["friend"]
    return jsonify({"status": "success", "friends": friend_data}), 200

@app.route('/getBio', methods=["POST"])
def getBio(): 
    mongo_id = request.json["mongo_id"]
    mongo_user = mongo.db.users.find_one({"username": username})
    bio = mongo_user["bio"]
    return jsonify({"status": "success", "bio": bio}), 200

@app.route('/getFormData', methods=["POST"])
def getFormData(): 
    mongo_id = request.json["mongo_id"]
    mongo_user = mongo.db.users.find_one({"username": username})
    formData = mongo_user["formData"]
    return jsonify({"status": "success", "formData": formData}), 200

#------------------- SOCKETS AYYYYYYYYYY ----------------#

socketConnections = {}

@socketio.on('connect', namespace="/websockets")
def connect(): 
    user_friend_code = request.args.get('friend_code')
    print(user_friend_code + " connected")
    socketConnections[user_friend_code] = request.sid

#  @io.on('disconnect')
#  def disconnect():
#      print "%s disconnected" % (request.namespace.socket.sessid)
#      socketConnections.remove(request.namespace)

@socketio.on('send_message', namespace="/websockets")
def handle_send_message(data): 
    message = data["message"]
    sender_friend_code = data["sender_friend_code"]
    receiver_friend_code = data["receiver_friend_code"]
    print("receiver: " + receiver_friend_code)
    if receiver_friend_code in socketConnections: 
        emit('receive_message', { 'message': message, 'friend_code': sender_friend_code }, room=socketConnections[receiver_friend_code])


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)

