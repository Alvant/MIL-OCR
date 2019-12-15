import gridfs
import json
import base64

from PIL import Image
from pymongo import MongoClient
from io import BytesIO
from pika import ConnectionParameters, \
                 BlockingConnection, \
                 BasicProperties
from bson import ObjectId


class TextExtractor:
    CORRECTOR_QUERY = "corrector"
    CORRECTOR_REPLY_QUERY = "corrector_reply"
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
            {"imageID": ObjectId(image_id)},
            {
                "$set": {"recognizedText": recognized_text}
            }
        )

    def put_corrected_text(self, image_id, recognized_text):
        self.collection.update_one(
            {"imageID": ObjectId(image_id)},
            {
                "$set": {"correctedText": recognized_text}
            }
        )

    def reply_corrector_handler(self, ch, method_frame, properties, body):
        message = json.loads(body.decode())
        self.put_corrected_text(message["imageID"], message["correctedText"])
        print("Received corrector reply: {:s}".format(message["imageID"]))

    def reply_ocr_handler(self, ch, method_frame, properties, body):
        message = json.loads(body.decode())
        self.put_recognized_text(message["imageID"], message["recognizedText"])
        ch.basic_publish(exchange="",
            routing_key=TextExtractor.CORRECTOR_QUERY,
            body=json.dumps(message),
            properties=BasicProperties(
                reply_to=TextExtractor.CORRECTOR_REPLY_QUERY))
        print("Received ocr reply: {:s}".format(message["imageID"]))

    def proccess_images(self):
        connection = BlockingConnection(ConnectionParameters(
            host="localhost"))

        channel = connection.channel()
        channel.queue_declare(
            queue=TextExtractor.OCR_REPLY_QUERY,
            auto_delete=True)
        channel.queue_declare(
            queue=TextExtractor.CORRECTOR_REPLY_QUERY,
            auto_delete=True)

        item = self.get_unhandled()[0]
        image = self.get_image(item["imageID"])

        with connection, channel:
            channel.basic_consume(
                TextExtractor.CORRECTOR_REPLY_QUERY,
                self.reply_corrector_handler,
                auto_ack=True)

            channel.basic_consume(
                TextExtractor.OCR_REPLY_QUERY,
                self.reply_ocr_handler,
                auto_ack=True)

            for _ in range(1):
                message = {
                    "imageID": str(item["imageID"]),
                    "image": base64.encodebytes(image).decode('ascii')
                }
                channel.basic_publish(exchange="",
                    routing_key=TextExtractor.OCR_QUERY,
                    body=json.dumps(message),
                    properties=BasicProperties(
                        reply_to=TextExtractor.OCR_REPLY_QUERY))

                print(" [x] Sent to image ocr")

            channel.start_consuming()


def main():
    exctractor = TextExtractor()
    exctractor.proccess_images()


if __name__ == "__main__":
    main()
