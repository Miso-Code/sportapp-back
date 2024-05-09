import boto3

from app.config.settings import Config


class SQS:
    def __init__(self, session: boto3.Session):
        self.sqs = session.client("sqs")

    def send_message(self, queue_name: str, message: str):
        self.sqs.send_message(QueueUrl=queue_name, MessageBody=message, MessageGroupId="nutritional_plan")
        print(f"Message sent {message}")


class AWSClient:
    def __init__(self):
        self.session = boto3.Session(region_name=Config.AWS_REGION)

        self.sqs = SQS(self.session)
