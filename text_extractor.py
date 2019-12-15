import gridfs
import json
import base64

from time import time
from pymongo import MongoClient
from pika import ConnectionParameters, \
                 BlockingConnection, \
                 BasicProperties
from bson import ObjectId
from tqdm import tqdm


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
        self.wait_for = None
        self.progress = None

    def add_image(self, path: str):
        with open(path, "rb") as f:
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

    def get_image(self, image_idx):
        img = self.fs.get(image_idx)
        return img.read()

    def put_recognized_text(self, idx, recognized_text):
        self.collection.update_one(
            {"_id": ObjectId(idx)},
            {
                "$set": {"recognizedText": recognized_text}
            }
        )

    def put_corrected_text(self, idx, recognized_text):
        self.collection.update_one(
            {"_id": ObjectId(idx)},
            {
                "$set": {"correctedText": recognized_text}
            }
        )

    def reply_corrector_handler(self, ch, method, properties, body):
        message = json.loads(body.decode())
        self.put_corrected_text(message["_id"], message["correctedText"])
        self.wait_for.remove(ObjectId(message["_id"]))
        self.progress.update()
        if len(self.wait_for) == 0:
            ch.stop_consuming()

    def reply_ocr_handler(self, ch, method, properties, body):
        message = json.loads(body.decode())
        if message["recognizedText"] is None:
            self.wait_for.remove(ObjectId(message["_id"]))
            self.progress.update()
            if len(self.wait_for) == 0:
                ch.stop_consuming()
            return

        self.put_recognized_text(message["_id"], message["recognizedText"])
        ch.basic_publish(
            exchange="",
            routing_key=TextExtractor.CORRECTOR_QUERY,
            body=json.dumps(message),
            properties=BasicProperties(
                reply_to=TextExtractor.CORRECTOR_REPLY_QUERY,
                delivery_mode=2
            ))

    def process_images(self):
        connection = BlockingConnection(ConnectionParameters(
            host="localhost"))

        channel = connection.channel()
        channel.queue_declare(
            queue=TextExtractor.OCR_REPLY_QUERY,
            auto_delete=True)
        channel.queue_declare(
            queue=TextExtractor.CORRECTOR_REPLY_QUERY,
            auto_delete=True)

        self.wait_for = set()
        with connection, channel:
            channel.basic_consume(
                TextExtractor.CORRECTOR_REPLY_QUERY,
                self.reply_corrector_handler,
                auto_ack=True)

            channel.basic_consume(
                TextExtractor.OCR_REPLY_QUERY,
                self.reply_ocr_handler,
                auto_ack=True)

            t = time()
            for item in self.get_unhandled():
                image = self.get_image(item["imageID"])
                message = {
                    "_id": str(item["_id"]),
                    "image": base64.encodebytes(image).decode('ascii')
                }
                channel.basic_publish(
                    exchange="",
                    routing_key=TextExtractor.OCR_QUERY,
                    body=json.dumps(message),
                    properties=BasicProperties(
                        reply_to=TextExtractor.OCR_REPLY_QUERY))

                self.wait_for.add(item["_id"])

            if len(self.wait_for) > 0:
                self.progress = tqdm(total=len(self.wait_for))
                channel.start_consuming()
                self.progress.close()
            print("All images are recognized. Time: {:.2f}".format(time() - t))


def main():
    extractor = TextExtractor()
    extractor.process_images()


if __name__ == "__main__":
    main()
