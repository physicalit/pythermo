import time, json
import paho.mqtt.client as paho
from cryptography.fernet import Fernet

# Import conf file
with open("config.json", "r") as f:
    paho_config = json.load(f)["paho"]

locals().update(paho_config)

f = Fernet(key.encode("utf-8"))

client= paho.Client("client-pub-opi001")
client.tls_set("/root/ca.crt")
client.username_pw_set(username, password)
client.connect(broker, port)


client.loop_start()

messagae = json.dumps([{'hmm':1}, "sergiu"])
client.publish("house/opi-001",f.encrypt(messagae.encode('utf-8')))



client.disconnect()
client.loop_stop()
