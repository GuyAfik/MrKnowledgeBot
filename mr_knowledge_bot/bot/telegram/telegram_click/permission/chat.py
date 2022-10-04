from telegram import Update
from telegram.ext import CallbackContext

from .base import Permission


class _PrivateChat(Permission):
    """
    Requires the interaction inside a private chat.
    """

    def evaluate(self, update: Update, context: CallbackContext) -> bool:
        chat_type = update.effective_chat.type
        return chat_type == 'private'


class _GroupChat(Permission):
    """
    Requires the interaction inside a group chat.
    """

    def evaluate(self, update: Update, context: CallbackContext) -> bool:
        chat_type = update.effective_chat.type
        return chat_type == 'group'


class _SuperGroupChat(Permission):
    """
    Requires the interaction inside a supergroup chat.
    """

    def evaluate(self, update: Update, context: CallbackContext) -> bool:
        chat_type = update.effective_chat.type
        return chat_type == 'supergroup'
