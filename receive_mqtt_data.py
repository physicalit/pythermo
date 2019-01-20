from multiprocessing import Process
import pymongo
import time, json
import paho.mqtt.client as paho
from cryptography.fernet import Fernet


with open("/opt/pythermo/config.json", "r") as f:
    srv_config = json.load(f)["srv"]

locals().update(srv_config)

f = Fernet(key.encode("utf-8"))

def insertMD(type, id, data):
    dbclient = pymongo.MongoClient()
    mydb = dbclient[type]
    mycol = mydb[id]
    mycol.insert_one(data)

# callback on_message
def on_message(client, userdata, message):
    result = json.loads(f.decrypt(message.payload).decode("utf-8"))
    insertMD(result["info"]["type"], result["info"]["id"], result["data"])

client= paho.Client("server-sub-001")
client.tls_set("/etc/mosquitto/tls/ca.crt")
client.username_pw_set(username, password)
client.on_message=on_message
client.connect(broker, port)

client.subscribe("house/senzor_data")
client.loop_forever()
# client.disconnect()
# client.loop_stop()
