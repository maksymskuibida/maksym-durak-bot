from durak.bot.shared.views import SendMessageView
from durak.user.domain.model.user import User


class StartCommandView(SendMessageView):
    def __init__(self, user: User):
        self.user = user

    async def get_text(self):
        return f'Hi, {self.user.first_name}!'
