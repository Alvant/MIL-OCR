import traceback

from jamspell import TSpellCorrector
from pika import BlockingConnection, ConnectionParameters


class Corrector:
    """
    Class receives messages and correct their text.
    """
    def __init__(self):
        self.corrector = TSpellCorrector()
        self.corrector.LoadLangModel('en.bin')

        self.connection = BlockingConnection(ConnectionParameters(
            host="rabbit"))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue="corrector", exclusive=True)
        print(" [*] Waiting for messages. To exit press CTRL+C")

        self.channel.basic_consume("corrector", self.callback)

    def correct(self, text: str):
        return self.corrector.FixFragment(text)

    def callback(self, ch, method, properties, body):
        print(" [x] Received by correcter {}".format(body))
        ch.basic_publish('',
            routing_key=properties.reply_to,
            body=self.correct(str(body)))
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
    corrector = Corrector()
    corrector.start()


if __name__ == "__main__":
    main()
