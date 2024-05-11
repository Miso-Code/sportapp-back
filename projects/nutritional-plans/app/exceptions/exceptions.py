class ExternalServiceError(Exception):
    def __init__(self, message="External service error"):
        super().__init__(message)
