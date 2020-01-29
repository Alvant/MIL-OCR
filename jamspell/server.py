import json
import os
import traceback
import warnings

from jamspell import TSpellCorrector
from pika import BlockingConnection, ConnectionParameters


class Corrector:
    """
    Class receives messages and correct their text.
    """
    def __init__(self, model_path: str):
        self.corrector = TSpellCorrector()

        is_model_loaded = self.corrector.LoadLangModel(model_path)

        if is_model_loaded is False:
            warnings.warn(
                f"Failed to load the model \"{model_path}\"!"
                " JamSpell is going to be useless without a model..."
            )

        self.connection = BlockingConnection(ConnectionParameters(
            host="rabbit"))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue="corrector")
        self.channel.basic_qos(prefetch_count=1)
        print(" [*] Waiting for messages. To exit press CTRL+C")
        self.channel.basic_consume("corrector", self.callback)

    def correct(self, text: str):
        return self.corrector.FixFragment(text)

    def callback(self, ch, method, properties, body):
        message = json.loads(body.decode())
        reply_message = {
            "_id": message["_id"],
            "correctedText": self.correct(message["recognizedText"])
        }
        print(" [x] Received by corrector {}".format(message["_id"]))
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
        except Exception:
            self.channel.stop_consuming()
            print("Error!!!\n", traceback.format_exc())


def main():
    config_file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '..',
        'config.json'
    )
    config = json.loads(open(config_file_path, 'r').read())

    corrector = Corrector(config["jamspell-model-path"])

    corrector.start()


if __name__ == "__main__":
    main()
