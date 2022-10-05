from typing import cast
import pytest
from unittest.mock import MagicMock
from telegram import Bot, Document, File, Message, PhotoSize, Update, User, CallbackQuery
from telegram.ext import CallbackContext


@pytest.fixture(name="telegram_user")
def fixture_telegram_user() -> User:
    user = cast(User, MagicMock())
    user.id = 123
    return user


@pytest.fixture()
def telegram_bot() -> Bot:
    return cast(Bot, MagicMock())


@pytest.fixture()
def callback_query() -> CallbackQuery:
    return cast(CallbackQuery, MagicMock())


@pytest.fixture(name="telegram_message")
def fixture_telegram_message(telegram_user: User) -> Message:
    msg = cast(Message, MagicMock())
    msg.from_user = telegram_user
    msg.text = "telegram_text"
    return msg


@pytest.fixture
def telegram_update(telegram_message: Message, callback_query: CallbackQuery) -> Update:
    update = cast(Update, MagicMock())
    update.effective_message = telegram_message
    update.callback_query = callback_query
    return update


@pytest.fixture
def telegram_context() -> CallbackContext:
    return cast(CallbackContext, MagicMock())
