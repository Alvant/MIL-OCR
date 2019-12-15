import traceback
import json
import base64

from io import BytesIO
from PIL import Image
from pytesseract import image_to_string
from pika import BlockingConnection, ConnectionParameters


class Recognizer:
    """
    Class receives image and extract text.
    """
    def __init__(self):
        self.connection = BlockingConnection(ConnectionParameters(
            host="rabbit"))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue="ocr")
        print(" [*] Waiting for messages. To exit press CTRL+C")
        self.channel.basic_consume("ocr", self.callback)

    def recognize(self, img):
        img = base64.decodebytes(img.encode('ascii'))
        image = Image.open(BytesIO(img))
        return image_to_string(image)

    def callback(self, ch, method, properties, body):
        message = json.loads(body.decode())
        print(" [x] Received image {} by ocr.".format(message["_id"]))
        ch.basic_publish("",
            routing_key=properties.reply_to,
            body=self.recognize(message["image"]))
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start(self):
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()
        except Exception:
            self.channel.stop_consuming()
            print("Error!!!\n", traceback.format_exc())


def main():
    recognizer = Recognizer()
    recognizer.start()


if __name__ == "__main__":
    main()
