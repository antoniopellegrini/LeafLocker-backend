class ValidationException(Exception):
    def __init__(self, *, message = "Parameters are invalid",errors = None) -> None:
        self.message = message
        self.errors = errors
    code = 422
    message = None