HICCUP_MESSAGE = 'Domain error occurred'


class DomainError(Exception):
    message: str = HICCUP_MESSAGE

    def resolve_message(self, message: str | None = None):
        return message or self.message

    def __init__(self, message: str | None = None):
        self.message = self.resolve_message(message)
        super().__init__(self.message)
