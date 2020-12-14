import cv2
import paho.mqtt.client as mqtt
import json


MQTT_HOST = '192.168.77.1'
MQTT_PORT = 1883
SUB_TOPICS = [
    ('/beverage/order', 2)
]

target = ''

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("connected OK")
    else:
        print("Bad connection Returned code=", rc)


def on_disconnect(client, userdata, flags, rc=0):
    print(str(rc))


def on_message(client, userdata, msg):
    global target

    data = json.loads(msg.payload.decode('utf-8'))

    if msg.topic == '/beverage/location':
        target = data['beverage']
        handle_qr()
    

def handle_qr():    
    detector = cv2.QRCodeDetector()
    cap = cv2.VideoCapture(0)

    while (cap.isOpened()):
        ret, img = cap.read()

        if (ret is False):
            break

        data, bbox, _ = detector.detectAndDecode(img)

        if (bbox is not None):
            if (data == target):
                client.publish('/qr', json.dumps({'qr': 'success'}), 2)

        cv2.imshow('img', img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':

    #MQTT Connection
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.connect(MQTT_HOST, MQTT_PORT)


    for topic in SUB_TOPICS:
        client.subscribe(topic[0], topic[1])
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        client.disconnect()
