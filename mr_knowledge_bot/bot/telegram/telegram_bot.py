
from abc import ABC
from mr_knowledge_bot.bot.base_bot import BaseBot
from telegram.ext import Updater
from telegram.ext import CommandHandler, CallbackContext
from telegram import Update
from mr_knowledge_bot.bot.telegram.telegram_click.decorator import command
from mr_knowledge_bot.bot.telegram.telegram_click.argument import Argument, Selection
from mr_knowledge_bot.bot.logic import MovieLogic, TVShowLogic


class TelegramBot(BaseBot, ABC):

    def __init__(self, token=None):
        super().__init__(token)
        self._updater = Updater(token=self.token, use_context=True)
        self._movie_commands_logic = MovieLogic()
        self._tv_shows_commands_logic = TVShowLogic()

        handler_groups = {
            1: [
                CommandHandler(command='find_movies_by_name', callback=self.find_movies_by_name_command),
                CommandHandler(command='find_tv_shows_by_name', callback=self.find_tv_shows_by_name_command)
            ]
        }

        for group, handlers in handler_groups.items():
            for handler in handlers:
                self._updater.dispatcher.add_handler(handler, group=group)

    def start(self):
        self._updater.start_polling()
        self._updater.idle()

    @command(
        name='find_movies_by_name',
        description='Allows you to find movies by name.',
        arguments=[
            Argument(
                name=['name', 'n'],
                description='The movie name to search for (can be substrings or partial movie names)',
                validator=lambda x: x.strip(),
                optional=False,
                type=str,
                example='-n "game of thrones"'
            ),
            Argument(
                name=['limit', 'l'],
                description='The maximum amount of movies to return, maximum is 50.',
                validator=lambda x: 50 >= x > 0,
                optional=True,
                type=int,
                example='-n "game of thrones" -l "20"',
                default=20,
            ),
            Selection(
                name=['sort-by', 's'],
                description='Sort by one of the following: popularity/release_date/rating.',
                optional=True,
                type=str,
                example='-n "game of thrones" -l "10" -s "release_date"',
                default='popularity',
                allowed_values=['popularity', 'release_date', 'rating']
            ),
        ]
    )
    def find_movies_by_name_command(
        self, update: Update, context: CallbackContext, name: str, limit: int, sort_by: str
    ):
        chat_id = update.message.chat_id
        context.bot.send_message(chat_id, text=f'Hang on while I am thinking, a bot needs to think too 🤓...')

        movie_names = self._movie_commands_logic.find_by_name(movie_name=name, limit=limit, sort_by=sort_by)
        if movie_names:
            text = f'Found the following movies for you 😀\n\n{movie_names}'
        else:
            text = f'Could not find any movies similar to the name "{name}" 😞'

        context.bot.send_message(chat_id, text=text)

    @command(
        name='find_tv_shows_by_name',
        description='Allows you to find tv-shows by name.',
        arguments=[
            Argument(
                name=['name', 'n'],
                description='The tv-show name to search for (can be substrings or partial tv-show names)',
                validator=lambda x: x.strip(),
                optional=False,
                type=str,
                example='-n "game of thrones"'
            ),
            Argument(
                name=['limit', 'l'],
                description='The maximum amount of tv-shows to return, maximum is 50.',
                validator=lambda x: 50 >= x > 0,
                optional=True,
                type=int,
                example='-n "game of thrones" -l "20"',
                default=20,
            ),
            Selection(
                name=['sort-by', 's'],
                description='Sort by one of the following: popularity/release_date/rating.',
                optional=True,
                type=str,
                example='-n "game of thrones" -l "10" -s "release_date"',
                default='popularity',
                allowed_values=['popularity', 'release_date', 'rating']
            ),
        ]
    )
    def find_tv_shows_by_name_command(
        self, update: Update, context: CallbackContext, name: str, limit: int, sort_by: str
    ):
        chat_id = update.message.chat_id
        context.bot.send_message(chat_id, text=f'Hang on while I am thinking, a bot needs to think too 🤓...')

        tv_shows_names = self._tv_shows_commands_logic.find_by_name(tv_show_name=name, limit=limit, sort_by=sort_by)
        if tv_shows_names:
            text = f'Found the following tv-shows for you 😀\n\n{tv_shows_names}'
        else:
            text = f'Could not find any tv-shows similar to the name "{name}" 😞'

        context.bot.send_message(chat_id, text=text)
