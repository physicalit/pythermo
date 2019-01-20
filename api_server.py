from flask import Flask, request
from flask_restful import Resource, Api, reqparse
import pymongo, json, sys, os, time
from datetime import datetime
sys.path.append('/opt/pythermo/')
os.chdir("/opt/pythermo/")


with open("config.json", "r") as f:
    api = json.load(f)["api"]

locals().update(api)
client = pymongo.MongoClient()
db = client['senzor_data']

os.environ['TZ'] = 'Europe/Bucharest'
time.tzset()

app = Flask(__name__)
api = Api(app)



class All_Senz(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('sensor_id', type=str)
        parser.add_argument('limit', type=int)
        param = parser.parse_args()
        if request.headers.get('Authorization') == token:
            result = []
            mycol = db[param["sensor_id"]]
            for entry in mycol.find():
                entry.pop('_id')
                try:
                    entry["timestamp"] = datetime.fromtimestamp(entry["timestamp"]).strftime('%Y-%m-%d %H:%M:%S')
                except KeyError:
                    continue
                result.append(entry)
            if param["limit"]:
                return result[-param["limit"]:], 200
            else:
                return result, 200
        else:
            return {'result': 'Not authorized'}, 401


api.add_resource(All_Senz, '/stats', endpoint='stats')


if __name__ == "__main__":
    app.run(port=5002)
