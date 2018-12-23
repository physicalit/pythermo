#!/usr/bin/python3
import pymongo, sys, os, json, time
import OPi.GPIO as GPIO
sys.path.append('/root/pythermo/')
os.chdir("/root/pythermo/")

with open("config.json", "r") as f:
    config = json.load(f)["config"]

locals().update(config)

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(5, GPIO.OUT)
GPIO.output(5, 0)

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
                time.sleep(360)
        elif out_temp > 0:
            if conf_temp - senz_temp >= 0.5:
                GPIO.output(5, 1)
                time.sleep(340)
                GPIO.output(5, 0)
                time.sleep(360)
        elif out_temp > -5:
            if conf_temp - senz_temp >= 0.5:
                GPIO.output(5, 1)
                time.sleep(300)
                GPIO.output(5, 0)
                time.sleep(360)
        elif out_temp < -5:
            if conf_temp - senz_temp >= 0.5:
                GPIO.output(5, 1)
                time.sleep(540)
                GPIO.output(5, 0)
                time.sleep(360)
        time.sleep(5)

termoStat()
