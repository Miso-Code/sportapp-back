import json
from time import sleep

from app.aws.aws import AWSClient
from app.config.settings import Config
from app.tasks.publisher import Publisher


class QueueProcessor:
    def __init__(self):
        self.sqs = AWSClient().sqs
        self.nutritional_plan_queue_name = Config.NUTRITIONAL_PLAN_ALERTS_QUEUE
        self.adverse_incidents_queue_name = Config.ADVERSE_INCIDENTS_ALERTS_QUEUE
        self.stop_thread = False

    def process_queues(self):
        while not self.stop_thread:
            self.process_queue(self.nutritional_plan_queue_name, "Nutritional Plan", "info")
            self.process_queue(self.adverse_incidents_queue_name, "Adverse Incident", "warning")
            sleep(0.5)

    def process_queue(self, queue_name: str, alert_type: str, alert_priority: str):
        messages = self.sqs.get_messages(queue_name)
        if messages:
            for message in messages.get("Messages", []):
                body = json.loads(message["Body"])
                print(f"Received {alert_type} message: {body}")
                Publisher.send_alert(body["user_id"], alert_priority, alert_type, body["message"])
                print("Alert sent!")
                self.sqs.delete_message(queue_name, message)
        return messages

    def stop_processing(self):
        self.stop_thread = True
