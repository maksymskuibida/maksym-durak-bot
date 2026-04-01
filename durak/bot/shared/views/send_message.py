from abc import ABC, abstractmethod

from aiogram import Bot, types
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import KeyboardBuilder

from durak.bot.shared.views import View


class SendMessageView(View, ABC):
    @staticmethod
    def _resolve_bot_and_chat_id(
        event: types.Message | types.CallbackQuery | None = None,
        bot: Bot | None = None,
        chat_id: int | None = None,
    ) -> tuple[Bot, int]:
        if event:
            if bot or chat_id:
                raise ValueError('You can not pass event and (bot, chat_id) together')

            if isinstance(event, types.Message):
                chat_id = event.from_user.id
            elif isinstance(event, types.CallbackQuery):
                chat_id = event.message.from_user.id
            else:
                raise ValueError('Unknown event type: ' + type(event).__name__)

            return event.bot, chat_id
        elif not bot:
            raise ValueError('You must pass bot or event')
        elif not chat_id:
            raise ValueError('You must pass chat_id')

        return bot, chat_id

    @abstractmethod
    async def get_text(self):
        raise NotImplementedError

    async def get_keyboard(self) -> types.ReplyMarkupUnion | KeyboardBuilder | None:
        return None

    async def get_sending_params(self):
        return {'parse_mode': ParseMode.HTML}

    async def send(
        self,
        event: types.Message | types.CallbackQuery | None = None,
        *,
        bot: Bot | None = None,
        chat_id: int | None = None,
    ) -> types.Message:
        sending_params = await self.get_sending_params()
        if 'text' in sending_params:
            raise ValueError('You can not pass text in sending_params')
        if 'reply_markup' in sending_params:
            raise ValueError('You can not pass reply_markup in sending_params')

        reply_markup = await self.get_keyboard()
        if isinstance(reply_markup, KeyboardBuilder):
            reply_markup = reply_markup.as_markup()

        bot, chat_id = self._resolve_bot_and_chat_id(event, bot, chat_id)

        return await bot.send_message(
            chat_id,
            await self.get_text(),
            reply_markup=reply_markup,
            **sending_params,
        )
