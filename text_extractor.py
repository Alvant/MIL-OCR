import gridfs
import json
import base64

from PIL import Image
from pymongo import MongoClient
from io import BytesIO
from pika import ConnectionParameters, \
                 BlockingConnection, \
                 BasicProperties


class TextExtractor:
    REPLY_QUERY = "amq.rabbitmq.reply-to"
    CORRECTOR_QUERY = "corrector"
    OCR_QUERY = "ocr"
    OCR_REPLY_QUERY = "ocr_reply"

    def __init__(self):
        self.client = MongoClient("localhost", 27017)
        self.db = self.client["image_db"]
        self.collection = self.db["image_collection"]
        self.fs = gridfs.GridFS(self.db)

    def add_image(self, path: str) -> None:
        with open("./img.png", "rb") as f:
            img = f.read()
        image_idx = self.fs.put(img)
        meta = {
            "imageID": image_idx,
            "recognizedText": None,
            "correctedText": None
        }

        self.collection.insert_one(meta)

    def get_unhandled(self):
        return self.collection.find({"recognizedText": None})

    def get_image(self, image_id):
        img = self.fs.get(image_id)
        return img.read()

    def put_recognized_text(self, image_id, recognized_text):
        self.collection.update_one(
            {"imageID": image_id},
            {
                "set": {"recognizedText": recognized_text}
            }
        )

    def put_corrected_text(self, image_id, recognized_text):
        self.collection.update_one(
            {"imageID": image_id},
            {
                "set": {"correctedText": recognized_text}
            }
        )

    def reply_handler(self, ch, method_frame, properties, body):
        print("Worker reply from correcter: {:s}".format(body.decode()))

    def reply_ocr_handler(self, ch, method_frame, properties, body):
        print("Worker reply from ocr: {:s}".format(body.decode()))

    def proccess_images(self):
        connection = BlockingConnection(ConnectionParameters(
            host="localhost"))
        channel = connection.channel()
        channel.queue_declare(queue=TextExtractor.OCR_REPLY_QUERY)
        item = self.get_unhandled()[0]
        image = self.get_image(item["imageID"])

        with connection, channel:
            channel.basic_consume(
                TextExtractor.REPLY_QUERY,
                self.reply_handler,
                auto_ack=True)

            channel.basic_consume(
                TextExtractor.OCR_REPLY_QUERY,
                self.reply_ocr_handler,
                auto_ack=True)

            for _ in range(1):
                message = {"_id": str(item["_id"]), "image": base64.encodebytes(image).decode('ascii')}
                channel.basic_publish(exchange="",
                    routing_key=TextExtractor.OCR_QUERY,
                    body=json.dumps(message),
                    properties=BasicProperties(reply_to=TextExtractor.REPLY_QUERY))

                print(" [x] Sent to image ocr")

            channel.start_consuming()


def main():
    exctractor = TextExtractor()
    exctractor.proccess_images()


if __name__ == "__main__":
    main()
