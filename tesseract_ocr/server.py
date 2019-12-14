import pika


def recognize(image):
    print("correction")
    pass


def callback(ch, method, properties, body):
    print(" [x] Received by ocr{}".format(body))


def run():
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host="rabbit"))
    channel = connection.channel()
    channel.queue_declare(queue="ocr")
    print(" [*] Waiting for messages. To exit press CTRL+C")
    channel.basic_consume("tmp", callback, auto_ack=True)
    channel.start_consuming()


if __name__ == "__main__":
    run()
