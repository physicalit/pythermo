import time, json, os, sys, calendar, datetime
import paho.mqtt.client as paho
from cryptography.fernet import Fernet
sys.path.append('/root/pythermo/')
os.chdir("/root/pythermo/")


# Import conf file
with open("config.json", "r") as f:
    main = json.load(f)

paho_config = main["paho"]
config = main["config"]

locals().update(paho_config)
locals().update(config)

if senzor_type == "dht22":
    from pyA20.gpio import gpio
    from pyA20.gpio import port as gport
    import dht22
elif senzor_type == "18b20":
    from w1thermsensor import W1ThermSensor
    sensor = W1ThermSensor()

def getSenzorTemp():
    timest = calendar.timegm(datetime.datetime.now().timetuple())
    if senzor_type == "dht22":
        while True:
            gpio.init()
            instance = dht22.DHT22(pin=gport.PA12)
            result = instance.read()
            if result.is_valid():
                return {
                        "info": {"type": "senzor_data",
                                 "id": id},
                        "data": {"temp": result.temperature,
                                 "humidity": result.humidity,
                                 "timestamp": timest}
                       }
    elif senzor_type == "18b20":
        temp = sensor.get_temperature()
        return {
                "info": {"type": "senzor_data",
                         "id": id},
                "data": {"temp": temp,
                         "timestamp": timest}
               }

f = Fernet(key.encode("utf-8"))

client= paho.Client(pub_client)
client.tls_set("/root/ca.crt")
client.username_pw_set(username, password)

while True:
    try:
        client.connect(broker, port)
        client.loop_start()
        messagae = json.dumps(getSenzorTemp())
        client.publish("house/senzor_data",f.encrypt(messagae.encode('utf-8')))
        client.disconnect()
        client.loop_stop()
        time.sleep(60)
    except OSError:
        continue
