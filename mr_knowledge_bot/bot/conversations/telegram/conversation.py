from abc import ABC, abstractmethod

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext


class Conversation(ABC):

    hang_on_message = f'Hang on while I am thinking, a bot needs to think too 🤓...'

    def __init__(self, update: Update, context: CallbackContext):
        self._update = update
        self._context = context

    @classmethod
    def from_stage(cls, update: Update, context: CallbackContext):
        return cls(update, context)

    def get_chat_id(self):
        message = self._update.message or self._update.callback_query.message
        return message.chat_id

    def get_message_id(self):
        message = self._update.callback_query.message or self._update.message or self._update.effective_message \
            or self._update.effective_message or self._update.message.reply_to_message
        return message.message_id

    @staticmethod
    def get_yes_or_no_keyboard():
        return InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text='Yes', callback_data='y'),
                    InlineKeyboardButton(text='No', callback_data='n')
                ]
            ]
        )
