#!/usr/bin/python3

from flask import Flask, request
from flask_restful import Resource, Api, reqparse

import pymongo, json
from datetime import datetime

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
            return {'resutl': 'Not authorized'}, 401

class All_Senz(Resource):
    def get(self, senz):
        parser = reqparse.RequestParser()
        if request.headers.get('Authorization') == token:
            result = []
            mycol = db[senz]
            for entry in mycol.find():
                entry.pop('_id')
                entry["timestamp"] = datetime.utcfromtimestamp(entry["timestamp"]).strftime('%Y-%m-%d %H:%M:%S')
                result.append(entry)
            return result, 200
        else:
            return {'resutl': 'Not authorized'}, 401

# class Employees_Name(Resource):
#     def get(self, employee_id):
#         conn = db_connect.connect()
#         query = conn.execute("select * from employees where EmployeeId =%d "  %int(employee_id))
#         result = {'data': [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}
#         return jsonify(result)


api.add_resource(Status, '/status') # Route_1
api.add_resource(All_Senz, '/status/<senz>') # Route_3


if __name__ == '__main__':
     app.run(port='5002', host='0.0.0.0')
