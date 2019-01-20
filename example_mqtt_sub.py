import time, json
import paho.mqtt.client as paho
from cryptography.fernet import Fernet

with open("config.json", "r") as f:
    paho_config = json.load(f)["paho"]

locals().update(paho_config)

f = Fernet(key.encode("utf-8"))
ms = []
# callback on_message
def on_message(client, userdata, message):
    global ms
    time.sleep(1)
    # ms.append(json.loads(message.payload.decode("utf-8")))
    # ms.append(f.decrypt(message.payload).decode("utf-8"))
    ms.append(json.loads(f.decrypt(message.payload).decode("utf-8")))

client= paho.Client("client-sub-001")
client.tls_set("/root/ca.crt")
client.username_pw_set(username, password)
client.on_message=on_message
client.connect(broker, port)


client.loop_start()
client.subscribe("house/opi-001")


client.disconnect()
client.loop_stop()
