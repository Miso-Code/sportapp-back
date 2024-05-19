import boto3

from app.config.settings import Config


class SQS:
    def __init__(self, session: boto3.Session):
        self.client = session.client("sqs")

    def get_messages(self, queue_name: str):
        messages = self.client.receive_message(QueueUrl=queue_name)
        return messages

    def delete_message(self, queue_name: str, message):
        self.client.delete_message(QueueUrl=queue_name, ReceiptHandle=message["ReceiptHandle"])
        print(f"Message deleted from {queue_name}")


class AWSClient:
    def __init__(self):
        self.session = boto3.Session(
            region_name=Config.AWS_REGION,
        )

        self.sqs = SQS(self.session)
