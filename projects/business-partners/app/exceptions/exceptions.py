class NotFoundError(Exception):
    pass


class EntityExistsError(Exception):
    pass


class InvalidValueError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class AWSException(Exception):
    pass
