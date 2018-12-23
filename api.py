#!/usr/bin/python3

from flask import Flask, request
from flask_restful import Resource, Api, reqparse

import pymongo, json
from datetime import datetime
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
                entry["timestamp"] = datetime.utcfromtimestamp(entry["timestamp"]).strftime('%Y-%m-%d %H:%M:%S')
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
                startHeat(run_time=param["time"])
                return {'result': 'Heater started for {} seconds'.format(param["time"])}
            else:
                startHeat()
                return {'result': 'Heater started'}
        else:
            return {'result': 'Not authorized'}, 401

api.add_resource(Status, '/status')
api.add_resource(All_Senz, '/stats', endpoint='stats')
api.add_resource(Start, '/start', endpoint='start')


if __name__ == '__main__':
     app.run(port='5002', host='0.0.0.0')
