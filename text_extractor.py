import gridfs

from PIL import Image
from pymongo import MongoClient
from io import BytesIO
from pika import ConnectionParameters, \
                 BlockingConnection, \
                 BasicProperties


class TextExtractor:
    REPLY_QUERY = 'amq.rabbitmq.reply-to'
    CORRECTOR_QUERY = "corrector"

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
            "edits": None
        }

        self.collection.insert_one(meta)

    def get_unhandled(self):
        return self.collection.find({'recognizedText': None})

    def get_image(self, image_id):
        img = self.fs.get(image_id)
        return Image.open(BytesIO(img.read()))

    def reply_handler(self, ch, method_frame, properties, body):
        print('RPC Client got reply: %s' % body)
        print('RPC Client says bye')

    def proccess_images(self):
        connection = BlockingConnection(ConnectionParameters(
            host='localhost'))
        channel = connection.channel()
        channel.queue_declare(queue="corrector")

        with connection, channel:
            channel.basic_consume(
                TextExtractor.REPLY_QUERY,
                self.reply_handler,
                auto_ack=True)

            for i in range(10):
                channel.basic_publish(exchange='',
                    routing_key=TextExtractor.CORRECTOR_QUERY,
                    body='Hello Womld!  ' + str(i),
                    properties=BasicProperties(reply_to=TextExtractor.REPLY_QUERY))

                print(" [x] Sent 'Hello World!'")

            channel.start_consuming()


def main():
    exctractor = TextExtractor()
    exctractor.proccess_images()


if __name__ == "__main__":
    main()
