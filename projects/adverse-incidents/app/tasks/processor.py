from logging import Logger
from time import sleep
from app.config.settings import Config
from app.services.adverse_incidents import AdverseIncidentsService


class Processor:
    def __init__(self, logger: Logger):
        self.stop_thread = False
        self.logger = logger
        self.adverse_incidents_service = AdverseIncidentsService()

    def process_incidents(self):
        while not self.stop_thread:
            try:
                message = self.adverse_incidents_service.process_incidents()
                self.logger.info(message)
            except Exception as e:
                self.logger.error(f"Error processing incidents: {str(e)}")
            self.logger.warning(f"Waiting {Config.NOTIFIER_SLEEP_TIME_SECONDS} seconds before processing next incidents")
            sleep(Config.NOTIFIER_SLEEP_TIME_SECONDS)

    def stop_processing(self):
        self.stop_thread = True
