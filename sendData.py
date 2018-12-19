#!/usr/bin/python3

from pyA20.gpio import gpio
from multiprocessing import Process
from pyA20.gpio import port
import time, sys
import http.client
import OPi.GPIO as GPIO
import pymongo, json
sys.path.append('/root/DHT22-Python-library-Orange-PI')
import dht22
import datetime, calendar

# init
GPIO.setmode(GPIO.BOARD)
GPIO.setup(5, GPIO.OUT)
GPIO.output(5, 0)
PIN2 = port.PA12

with open("config.json", "r") as f:
    config = json.load(f)["config"]

locals().update(config)

def writeToMongo(coll, data):
    client = pymongo.MongoClient()
    client = pymongo.MongoClient(mon_host, username=mon_user, password=mon_pass)
    db = client['termostat']
    collection = getattr(db, coll)
    post_id = collection.insert_one(data).inserted_id
    post_id
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
                writeToMongo("senzor1", {"temp": result.temperature, "humidity": result.humidity, "timestamp": timest})
            except:
                continue
            time.sleep(60)


def outTemp():
    print('func2: starting')
    while True:
        try:
            conn = http.client.HTTPConnection("api.openweathermap.org")
            headers = {
                'x-api-key': "5354ce02471f271dfe733ff8c524bffe",
                'cache-control': "no-cache",
                'postman-token': "65db4602-6cdc-eded-62c1-7c372ee02971"
                }
            conn.request("GET", "/data/2.5/weather?q=Dobroesti&units=metric", headers=headers)
            res = conn.getresponse()
            result = json.load(res)["main"]
            result["timestamp"] = calendar.timegm(datetime.datetime.now().timetuple())
            writeToMongo("senzor_out", result)
        except:
            continue
        time.sleep(60)

if __name__ == '__main__':
    p1 = Process(target=getSenzorMain, args=(gpio,))
    p2 = Process(target=outTemp)
    p1.start()
    p2.start()


# print("Last valid input: " + str(datetime.datetime.utcfromtimestamp(timest).strftime('%Y-%m-%d %H:%M:%S')))