#!/usr/bin/python3

from multiprocessing import Process
import datetime, calendar, socket
import time, sys, subprocess, os
import http.client
import requests
import pymongo, json
sys.path.append('/root/pythermo/')
os.chdir("/root/pythermo/")
import OPi.GPIO as GPIO
from pyA20.gpio import gpio
from pyA20.gpio import port
import dht22

# sys.path.append('/root/DHT22-Python-library-Orange-PI')
# init pins
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(5, GPIO.OUT)
GPIO.output(5, 0)
PIN2 = port.PA12

# load config file
with open("config.json", "r") as f:
    config = json.load(f)["config"]

locals().update(config)

# If no internet connexion restart the orange pi
def is_connected():
    while True:
        try:
            host = socket.gethostbyname("www.google.com")
            s = socket.create_connection((host, 80), 2)
            time.sleep(30)
        except KeyboardInterrupt:
            pass
        except:
            subprocess.run(["reboot"])

# define functions
def writeToMongo(coll, data):
    # client = pymongo.MongoClient()
    client = pymongo.MongoClient(host=mon_host, port=mon_port, username=mon_user,
                                 password=mon_pass, authSource=mon_authSource)
    db = client['termostat']
    collection = getattr(db, coll)
    post_id = collection.insert_one(data).inserted_id
    db.collection_names(include_system_collections=False)

def getSenzorMain(gpio):
    while True:
        gpio.init()
        instance = dht22.DHT22(pin=PIN2)
        # print('func1: starting')
        result = instance.read()
        if result.is_valid():
            timest = calendar.timegm(datetime.datetime.now().timetuple())
            try:
                writeToMongo("senzor1", {"temp": result.temperature,
                                         "humidity": result.humidity,
                                         "timestamp": timest})
            except:
                continue
            print({"temp": result.temperature, "humidity": result.humidity,
                   "timestamp": timest})
            time.sleep(60)

def outTemp():
    # print('func2: starting')
    while True:
        try:
            url = "http://api.openweathermap.org/data/2.5/weather"
            payload = ""
            headers = {
                'x-api-key': api_key,
                'cache-control': "no-cache",
                }
            response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
            result = json.loads(response.text)["main"]
            result["timestamp"] = calendar.timegm(datetime.datetime.now().timetuple())
            writeToMongo("senzor_out", result)
            print(result)
        except:
            continue
        time.sleep(60)

def startHeat(run_time=300):
    GPIO.output(5, 1)
    time.sleep(run_time)
    GPIO.output(5, 0)

# execute the script
if __name__ == '__main__':
    p1 = Process(target=getSenzorMain, args=(gpio,))
    p2 = Process(target=outTemp)
    p3 = Process(target=is_connected)
    p1.start()
    p2.start()
    p3.start()


# print("Last valid input: " + str(datetime.datetime.utcfromtimestamp(timest).strftime('%Y-%m-%d %H:%M:%S')))
