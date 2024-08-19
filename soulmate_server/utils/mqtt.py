# mqtt_utils.py
import paho.mqtt.client as mqtt

from soulmate_server.conf.dataConf import mqttList, mqttConf


class MqttClient:
    _instance = None

    def __new__(cls, broker_host, broker_port, username=None, password=None):
        if not cls._instance:
            cls._instance = super(MqttClient, cls).__new__(cls)
            cls._instance.client = mqtt.Client()
            cls._instance.client.on_connect = cls._instance.on_connect
            cls._instance.client.on_message = cls._instance.on_message

            if username and password:
                cls._instance.client.username_pw_set(username, password)

            cls._instance.broker_host = broker_host
            cls._instance.broker_port = broker_port

            cls._instance.client.connect(cls._instance.broker_host, cls._instance.broker_port, 60)
            cls._instance.client.loop_start()

        return cls._instance

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {rc}")
        # You can subscribe to topics or perform other setup actions here

        self.subscribe("soulmate")

    def on_message(self, client, userdata, msg):
        print(f"Received message: {msg.payload}")

    def publish(self, topic, message):
        self.client.publish(topic, message)
    async def asyncPublish(self, topic, message):
        self.client.publish(topic, message)
    def subscribe(self, topic):
        self.client.subscribe(topic)

    @classmethod
    def get_instance(cls):
        return cls._instance


mqttCo = MqttClient(broker_host=mqttConf['host'], broker_port=mqttConf['port'],password=mqttConf['password'],username=mqttConf['username'])


def get_mq():
    mq = mqttCo()
    try:
        yield mq
    finally:
        mq.close()
