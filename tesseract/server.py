import base64
import json
import os
import traceback

from io import BytesIO
from PIL import Image
from pytesseract import image_to_string
from pika import BlockingConnection, ConnectionParameters


class Recognizer:
    """
    Class receives image and extract text.
    """

    SUPPORTED_FORMATS = ["PNG", "JPEG"]

    def __init__(self, language: str, encoding: str):
        self.connection = BlockingConnection(
            ConnectionParameters(host="rabbit")
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue="ocr")
        self.channel.basic_qos(prefetch_count=1)

        self.language = language
        self.encoding = encoding

        print(" [*] Waiting for messages. To exit press CTRL+C")

        self.channel.basic_consume("ocr", self.callback)

    def recognize(self, img):
        try:
            img = base64.decodebytes(img.encode(self.encoding))
            image = Image.open(BytesIO(img))
            if image.format in Recognizer.SUPPORTED_FORMATS:
                return image_to_string(image, lang=self.language)
        except:
            print("Can't open image. It's really image?")
        
        return None

    def callback(self, ch, method, properties, body):
        message = json.loads(body.decode())
        reply_message = {
            "_id": message["_id"],
            "recognizedText": self.recognize(message["image"])
        }
        print(" [x] Received image {} by ocr.".format(message["_id"]))
        ch.basic_publish(
            "",
            routing_key=properties.reply_to,
            body=json.dumps(reply_message))
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start(self):
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()
        except Exception as e:
            self.channel.stop_consuming()
            print("Error!!!\n", traceback.format_exc())


def main():
    config_file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'config.json'
    )
    config = json.loads(open(config_file_path, 'r').read())

    recognizer = Recognizer(
        config['language'],
        config['image-bytes-encoding']
    )

    recognizer.start()


if __name__ == "__main__":
    main()
