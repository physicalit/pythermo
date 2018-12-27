#!/usr/bin/python3
from multiprocessing import Process
from flask import Flask, request
from flask_restful import Resource, Api, reqparse

import pymongo, json, sys, os
from datetime import datetime
sys.path.append('/root/pythermo/')
os.chdir("/root/pythermo/")
from sendData import startHeat


with open("config.json", "r") as f:
    api = json.load(f)["api"]

locals().update(api)

with open("config.json", "r") as f:
    config = json.load(f)["config"]

locals().update(config)


# Conn to mongo
client = pymongo.MongoClient(host=mon_host, port=mon_port, username=mon_user,
                             password=mon_pass, authSource=mon_authSource)
db = client['termostat']


app = Flask(__name__)
api = Api(app)

class Status(Resource):
    def get(self):
        if request.headers.get('Authorization') == token:
            OUT_TEMP = []
            SENZ1_TEMP = []
            mycol = db["senzor1"]
            for entry in mycol.find():
                SENZ1_TEMP.append(entry)
            mycol = db["senzor_out"]
            for entry in mycol.find():
                OUT_TEMP.append(entry)
            result = [SENZ1_TEMP[len(SENZ1_TEMP)-1], OUT_TEMP[len(OUT_TEMP)-1]]
            for l in result:
                l["timestamp"] = datetime.utcfromtimestamp(l["timestamp"]).strftime('%Y-%m-%d %H:%M:%S')
                l.pop('_id')
            return result, 200
        else:
            return {'result': 'Not authorized'}, 401

class All_Senz(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('senzor_name', type=str)
        parser.add_argument('limit', type=int)
        param = parser.parse_args()
        if request.headers.get('Authorization') == token:
            result = []
            try:
                mycol = db[param["senzor_name"]]
            except:
                return {'result': 'No such senzor, or not specified'}, 404
            for entry in mycol.find():
                entry.pop('_id')
                try:
                    entry["timestamp"] = datetime.utcfromtimestamp(entry["timestamp"]).strftime('%Y-%m-%d %H:%M:%S')
                except KeyError:
                    continue
                result.append(entry)
            if param["limit"]:
                return result[-param["limit"]:], 200
            else:
                return result, 200
        else:
            return {'result': 'Not authorized'}, 401

class Start(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('time', type=int)
        param = parser.parse_args()
        if request.headers.get('Authorization') == token:
            if param["time"]:
                p1 = Process(target=startHeat, args=(param["time"],))
                return {'result': 'Heater started for {} seconds'.format(param["time"])}
            else:
                p1 = Process(target=startHeat, args=(300,))
                return {'result': 'Heater started'}
            p1.start()
        else:
            return {'result': 'Not authorized'}, 401
class SetTemp(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('temperature', type=int)
        parser.add_argument('loc', type=int)
        param = parser.parse_args()
        if request.headers.get('Authorization') == token:
            if param["temperature"]:
                if param["loc"] == 0:
                    mycol = db["config"]
                    for entry in mycol.find():
                        obj = entry
                    mycol.update(obj, {"$set": {'temp': param["temperature"]}}, upsert=False)
                    for entry in mycol.find():
                        entry.pop('_id')
                        return entry
                if param["loc"] == 1:
                    mycol = db["config2"]
                    for entry in mycol.find():
                        obj = entry
                    mycol.update(obj, {"$set": {'temp': param["temperature"]}}, upsert=False)
                    for entry in mycol.find():
                        entry.pop('_id')
                        return entry
            else:
                return {'result': 'No temperature specified'}, 404
        else:
            return {'result': 'Not authorized'}, 401

api.add_resource(Status, '/status')
api.add_resource(All_Senz, '/stats', endpoint='stats')
api.add_resource(Start, '/start', endpoint='start')
api.add_resource(SetTemp, '/temp', endpoint='temp')


if __name__ == '__main__':
     app.run(port='5002', host='0.0.0.0')
