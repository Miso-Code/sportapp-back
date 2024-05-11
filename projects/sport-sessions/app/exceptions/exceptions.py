class NotFoundError(Exception):
    def __init__(self, message="Resource not found"):
        super().__init__(message)


class NotActiveError(Exception):
    def __init__(self, message="Resource not active"):
        super().__init__(message)


class InvalidApiKeyError(Exception):
    def __init__(self, message="Invalid API Key"):
        super().__init__(message)
