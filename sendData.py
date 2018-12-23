#!/usr/bin/python3

from multiprocessing import Process
import datetime, calendar, socket
import time, sys, subprocess
import http.client
import pymongo, json
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
            conn = http.client.HTTPConnection("api.openweathermap.org")
            headers = {
                'x-api-key': api_key,
                'cache-control': "no-cache",
                }
            conn.request("GET", req_param, headers=headers)
            res = conn.getresponse()
            result = json.load(res)["main"]
            result["timestamp"] = calendar.timegm(datetime.datetime.now().timetuple())
            writeToMongo("senzor_out", result)
            print(result)
        except:
            continue
        time.sleep(60)

def termoStat():
    client = pymongo.MongoClient(host=mon_host, port=mon_port, username=mon_user,
    password=mon_pass, authSource=mon_authSource)
    db = client['termostat']
    while True:
        mycol = db["config"]
        for entry in mycol.find():
            conf_temp = entry['temp']
        mycol = db["senzor1"]
        for senz_temp in mycol.find():
            senz_temp = senz_temp["temp"]
        mycol = db["senzor_out"]
        for out_temp in mycol.find():
            out_temp = out_temp["temp"]
        if out_temp > 5:
            if conf_temp - senz_temp >= 1:
                GPIO.output(5, 1)
            time.sleep(180)
            GPIO.output(5, 0)
        elif out_temp > 0:
            if conf_temp - senz_temp >= 0.5:
                GPIO.output(5, 1)
            time.sleep(340)
            GPIO.output(5, 0)
        elif out_temp > -5:
            if conf_temp - senz_temp >= 0.5:
                GPIO.output(5, 1)
            time.sleep(300)
            GPIO.output(5, 0)
        elif out_temp < -5:
            if conf_temp - senz_temp >= 0.5:
                GPIO.output(5, 1)
            time.sleep(540)
            GPIO.output(5, 0)
        time.sleep(5)


def startHeat(run_time=300):
    GPIO.output(5, 1)
    time.sleep(run_time)
    GPIO.output(5, 0)

# execute the script
if __name__ == '__main__':
    p1 = Process(target=getSenzorMain, args=(gpio,))
    p2 = Process(target=outTemp)
    p3 = Process(target=is_connected)
    p4 = Process(target=termoStat)
    p1.start()
    p2.start()
    p3.start()
    p4.start()


# print("Last valid input: " + str(datetime.datetime.utcfromtimestamp(timest).strftime('%Y-%m-%d %H:%M:%S')))
