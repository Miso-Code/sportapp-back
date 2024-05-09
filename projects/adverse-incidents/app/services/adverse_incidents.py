import json
from typing import List

from botocore.exceptions import ClientError
from app.aws.aws import AWSClient
from app.config.settings import Config
from app.exceptions.exceptions import ExternalServiceError
from app.models.schemas.schema import AdverseIncidentMessage, AdverseIncident, UserTraining
from app.services.external import ExternalServices
from app.utils import utils


def _get_users_affected_by_incident(incident: AdverseIncident, users_training: List[UserTraining]):
    users_affected = []
    for user in users_training:
        if utils.is_user_in_bounding_box(user, incident.bounding_box):
            users_affected.append(user.user_id)
    return users_affected


class AdverseIncidentsService:
    def __init__(self):
        self.sqs = AWSClient().sqs
        self.external_services = ExternalServices()
        self.adverse_incidents_queue_name = Config.ADVERSE_INCIDENTS_ALERTS_QUEUE

    def _notify_adverse_incident(self, message: AdverseIncidentMessage):
        self.sqs.send_message(self.adverse_incidents_queue_name, json.dumps(message.dict()))

    def _process_adverse_incident(self, incident: AdverseIncident, users_training: List[UserTraining]):
        users_affected = _get_users_affected_by_incident(incident, users_training)
        for user_id in users_affected:
            self._notify_adverse_incident(AdverseIncidentMessage(user_id=user_id, message=incident.description))
        return len(users_affected)

    def process_incidents(self):
        try:
            users_training_json = self.external_services.get_users_training()
            users_training = [UserTraining(**user) for user in users_training_json]
            incidents = self.external_services.get_incidents()
            users_notified = 0
            for incident in incidents:
                users_notified += self._process_adverse_incident(AdverseIncident(**incident), users_training)

            return {"message": f"Processed {len(incidents)} incidents and notified {users_notified} users."}

        except ExternalServiceError as e:
            return {"message": f"Failed to process incidents: {str(e)}"}

        except ClientError as e:
            return {"message": f"Error processing incidents: {str(e)}"}
