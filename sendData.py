#!/usr/bin/python3

from multiprocessing import Process
import datetime, calendar
import time, sys
import http.client
import pymongo, json
import OPi.GPIO as GPIO
from pyA20.gpio import gpio
from pyA20.gpio import port
import dht22

# sys.path.append('/root/DHT22-Python-library-Orange-PI')
# init pins
GPIO.setmode(GPIO.BOARD)
GPIO.setup(5, GPIO.OUT)
GPIO.output(5, 0)
PIN2 = port.PA12

# load config file
with open("config.json", "r") as f:
    config = json.load(f)["config"]

locals().update(config)


# define functions
def writeToMongo(coll, data):
    client = pymongo.MongoClient()
    client = pymongo.MongoClient(mon_host, username=mon_user, password=mon_pass)
    db = client['termostat']
    collection = getattr(db, coll)
    post_id = collection.insert_one(data).inserted_id
    db.collection_names(include_system_collections=False)

def getSenzorMain(gpio):
    while True:
        gpio.init()
        instance = dht22.DHT22(pin=PIN2)
        print('func1: starting')
        result = instance.read()
        if result.is_valid():
            timest = calendar.timegm(datetime.datetime.now().timetuple())
            try:
                writeToMongo("senzor1", {"temp": result.temperature,
                                         "humidity": result.humidity,
                                         "timestamp": timest})
            except:
                continue
            time.sleep(60)

def outTemp():
    print('func2: starting')
    while True:
        try:
            conn = http.client.HTTPConnection("api.openweathermap.org")
            headers = {
                'x-api-key': x-api-key,
                'cache-control': "no-cache",
                }
            conn.request("GET", req_param, headers=headers)
            res = conn.getresponse()
            result = json.load(res)["main"]
            result["timestamp"] = calendar.timegm(datetime.datetime.now().timetuple())
            writeToMongo("senzor_out", result)
        except:
            continue
        time.sleep(60)

# execute the script
if __name__ == '__main__':
    p1 = Process(target=getSenzorMain, args=(gpio,))
    p2 = Process(target=outTemp)
    p1.start()
    p2.start()


# print("Last valid input: " + str(datetime.datetime.utcfromtimestamp(timest).strftime('%Y-%m-%d %H:%M:%S')))
