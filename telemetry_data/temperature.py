import paho.mqtt.client as mqtt
from datetime import datetime
import time
import board
import adafruit_dht
import config as cf

broker = cf.broker
mqtt_topic = cf.mqtt_topic

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

client = mqtt.Client()
client.on_connect = on_connect
#client.on_message = on_message
client.connect(broker)
client.loop_start()

# Initial the dht device, with data pin connected to:
dhtDevice = adafruit_dht.DHT11(board.D4)

# Could set this granularity to whatever we want based on device, monitoring needs, etc
temperature = 0
humidity = 0
pressure = 0

while True:
    try:
        telemetry_time = datetime.today()
        dt = telemetry_time.strftime("%Y-%m-%d") 
        tm = telemetry_time.strftime("%H:%M:%S")
        cur_temp = dhtDevice.temperature
        cur_humidity = dhtDevice.humidity

        if cur_temp == temperature and cur_humidity == humidity:
            time.sleep(1)
            continue

        temperature = cur_temp
        humidity = cur_humidity

        payload = '{{ "dt": "{}", "tm": "{}", "temperature": {}, "humidity": {} }}'.format(dt, tm, temperature, humidity)

        client.publish(mqtt_topic, payload, qos=1)

        print("{}\n".format(payload))

        time.sleep(1)
        
    except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just keep going
        print(error.args[0])

client.loop_stop()
