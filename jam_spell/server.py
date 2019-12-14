import pika


def correct(text):
    print("correction")
    pass


def callback(ch, method, properties, body):
    print(" [x] Received by correcter {}".format(body))


def run():
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host="rabbit"))
    channel = connection.channel()
    channel.queue_declare(queue="corrector")
    print(" [*] Waiting for messages. To exit press CTRL+C")
    channel.basic_consume("tmp", callback, auto_ack=True)
    channel.start_consuming()


if __name__ == "__main__":
    run()
