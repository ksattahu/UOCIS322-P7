# Streaming Service
from flask import Flask, jsonify, request, abort, Response
from flask_restful import Resource, Api
from pymongo import MongoClient
import os
from itsdangerous import (TimedJSONWebSignatureSerializer \
                                  as Serializer, BadSignature, \
                                  SignatureExpired)
from passlib.hash import sha256_crypt as pwd_context


client = MongoClient('mongodb://' + os.environ['MONGODB_HOSTNAME'], 27017)
db = client.brevetsdb
dbu = client.usersdb

app = Flask(__name__)
api = Api(app)

SECRET_KEY = 'test1234@#$'


def generate_auth_token(id, username, password, expiration=600):
    s = Serializer(SECRET_KEY, expires_in=expiration)
    return s.dumps({"id": id, "username": username, "password": password})


def verify_auth_token(token):
    s = Serializer(SECRET_KEY)
    try:
        data = s.loads(token)
    except SignatureExpired:
        return False    # valid token, but expired
    except BadSignature:
        return False    # invalid token
    return True

class register(Resource):
    def post(self):
        username = request.args.get("username", type=str)
        password = pwd_context.using(salt="somestring").encrypt(request.args.get("password"))
        if not dbu.usersdb.find_one({"username": username}):
            entry = {
                    "id": int(dbu.usersdb.count_documents({})) + 1,
                    "username": username,
                    "password": password
                    }
            dbu.usersdb.insert_one(entry)
            app.logger.debug(f"{dbu.usersdb.find_one({'username': username})}")
            return Response(status=201)
        return Response(status=400)


class token(Resource):
    def get(self, duration=600):
        username = request.args.get("username", type=str)
        password = request.args.get("password", type=str)
        u = dbu.usersdb.find_one({"username": username})
        if dbu.usersdb.find_one({"username": username}) and pwd_context.verify(password, u["password"]):
            response = {
                    "id": u["id"],
                    "token": generate_auth_token(u["id"], u["username"], u["password"], duration).decode('utf-8'),
                    "duration": duration
                    }
            return response, 201
        return Response(status=401)


class listAll(Resource):
    def get(self, data="json"):
        token = request.args.get("token")
        if not verify_auth_token(token):
            return Response(status=401)
        k = int(request.args.get("top", default=-1))
        vals = list(db.vals.find({}, {'_id': 0, 'brevet_dist': 0, 'begin_date': 0, 'km': 0, 'miles': 0, 'location': 0}))
        if data == "json":
            return _json(k, vals)
        else:
            return _csv(k, vals)


class listOpenOnly(Resource):
    def get(self, data="json"):
        token = request.args.get("token")
        if not verify_auth_token(token):
            return Response(status=401)
        k = int(request.args.get("top", default=-1))
        vals = list(db.vals.find({}, {'_id': 0, 'brevet_dist': 0, 'begin_date': 0, 'km': 0, 'miles': 0, 'location': 0, 'close_time': 0}))
        if data == "json":
            return _json(k, vals)
        else:
            return _csv(k, vals)


class listCloseOnly(Resource):
    def get(self, data="json"):
        token = request.args.get("token")
        if not verify_auth_token(token):
            return Response(status=401)
        k = int(request.args.get("top", default=-1))
        vals = list(db.vals.find({}, {'_id': 0, 'brevet_dist': 0, 'begin_date': 0, 'km': 0, 'miles': 0, 'location': 0, 'open_time': 0}))
        if data == "json":
            return _json(k, vals)
        else:
            return _csv(k, vals)

def _json(k, vals):
    if k >= 0 and k <= len(vals):
        ret = []
        for i in range(k):
            ret.append(dict(vals[i]))
        return jsonify(ret)
    return jsonify(vals)


def _csv(k, vals):
    times = list(vals[0].keys())
    temp = []
    if k < 0 or k > len(vals):
        k = len(vals)
    for i in range(k):
        for time in times:
            if time == times[-1]:
                temp.append(str((vals[i]).get(time) + "\n"))
            else:
                temp.append(str((vals[i]).get(time)))
    return ",".join(times) + "\n" + ",".join(temp)


# Create routes
# Another way, without decorators
api.add_resource(listAll, '/listAll', '/listAll/', '/listAll/<string:data>')
api.add_resource(listOpenOnly, '/listOpenOnly', '/listOpenOnly/', '/listOpenOnly/<string:data>')
api.add_resource(listCloseOnly, '/listCloseOnly', '/listCloseOnly/', '/listCloseOnly/<string:data>')
api.add_resource(register, '/register')
api.add_resource(token, '/token')

# Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
