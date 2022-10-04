from abc import ABC

from telegram import ParseMode, ReplyKeyboardRemove, Update
from telegram.ext import (CallbackContext, CallbackQueryHandler,
                          CommandHandler, ConversationHandler, Filters,
                          MessageHandler, Updater)

from mr_knowledge_bot.bot.base_bot import BaseBot
from mr_knowledge_bot.bot.conversations import MovieConversation
from mr_knowledge_bot.bot.telegram.telegram_click import generate_command_list
from mr_knowledge_bot.bot.telegram.telegram_click.argument import (Argument,
                                                                   Flag,
                                                                   Selection)
from mr_knowledge_bot.bot.telegram.telegram_click.decorator import command


class TelegramBot(BaseBot, ABC):

    def __init__(self, token=None):
        super().__init__(token)
        self._updater = Updater(token=self.token, use_context=True)

        self._movie_conversation = MovieConversation

        movies_conversation_handler = ConversationHandler(
            entry_points=[
                CommandHandler(command='find_movies_by_name',
                               callback=self.find_movies_by_name_command),
                CommandHandler(command='discover_movies',
                               callback=self.discover_movies_command),
            ],
            states={
                self._movie_conversation.query_movie_details_stage: [
                    CallbackQueryHandler(callback=self.query_movie_overview)
                ],
                self._movie_conversation.display_movie_details_stage: [
                    MessageHandler(filters=Filters.regex(
                        '^(?!.*exit).*$'), callback=self.display_movie_overview)
                ],
                self._movie_conversation.query_movie_for_trailer_stage: [
                    CallbackQueryHandler(callback=self.query_movie_trailer)
                ],
                self._movie_conversation.display_movie_trailer_stage: [
                    MessageHandler(filters=Filters.regex(
                        '^(?!.*exit).*$'), callback=self.display_movie_trailer)
                ]
            },
            fallbacks=[MessageHandler(filters=Filters.regex(
                '^exit$'), callback=self.cancel_conversation)],
            allow_reentry=True
        )

        handler_groups = {
            0: [
                CommandHandler(command='help', callback=self.help_command),
                movies_conversation_handler,
                # CommandHandler(command='find_tv_shows_by_name', callback=self.find_tv_shows_by_name_command),
                # CommandHandler(command='discover_tv_shows', callback=self.discover_tv_shows_command),
                # CommandHandler(command='get_movie_genres', callback=self.get_movie_genres_command),
                # CommandHandler(command='get_tv_shows_genres', callback=self.get_tv_shows_genres_command)
            ],
            # 1: [
            #     MessageHandler(Filters.text & ~Filters.command, callback=self._unknown_command)
            # ]
        }

        for group, handlers in handler_groups.items():
            for handler in handlers:
                self._updater.dispatcher.add_handler(handler, group=group)

    def start(self):
        self._updater.start_polling()
        self._updater.idle()

    def cancel_conversation(self, update: Update, context: CallbackContext):
        self.send_available_commands(update, context)
        return ConversationHandler.END

    def _unknown_command(self, update: Update, context: CallbackContext):
        self.send_available_commands(update, context)

    @command(name=['help'], description='List the conversations supported by the MrKnowledgeBot')
    def help_command(self, update: Update, context: CallbackContext):
        self.send_available_commands(update, context)

    @staticmethod
    def send_available_commands(update: Update, context: CallbackContext):
        bot = context.bot
        chat_id = update.effective_message.chat_id

        user_info = update.message.from_user
        first_name = user_info.first_name
        last_name = user_info.last_name

        text = f'Hello {first_name} {last_name}! Here are the available conversations 😎' \
               f'\n\n{generate_command_list(update, context, summary=True)}'
        bot.send_message(chat_id, text, parse_mode=ParseMode.MARKDOWN)

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
                description='The maximum amount of movies to return, maximum is 100.',
                validator=lambda x: 100 >= x > 0,
                optional=True,
                type=int,
                example='-n "game of thrones" -l "20"',
                default=50,
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
        return self._movie_conversation(update, context).find_movies_by_name_command(
            name=name, limit=limit, sort_by=sort_by
        )

    @command(
        name='discover_movies',
        description='Allows you to discover movies by several options.',
        arguments=[
            Argument(
                name=['limit', 'l'],
                description='The maximum amount of movies to return, maximum is 100.',
                validator=lambda x: 100 >= x > 0,
                optional=True,
                type=int,
                example='-l "80"',
                default=50,
            ),
            Selection(
                name=['sort-by', 's'],
                description='Sort by one of the allowed values',
                optional=True,
                type=str,
                example='-s "popularity"',
                default='popularity',
                allowed_values=['popularity', 'release_date', 'rating']
            ),
            Argument(
                name=['before_date', 'bd'],
                description='Movies that were released before '
                            'the specified date in the form of a date. "year-month-day"',
                optional=True,
                example='-bd "2014-09-13"',
                type=str
            ),
            Argument(
                name=['after_date', 'ad'],
                description='Movies that were released after '
                            'the specified date in the form of a date. "year-month-day"',
                optional=True,
                example='-ad "2014-09-13"',
                type=str
            ),
            Argument(
                name=['with_genres', 'wg'],
                description='Comma-separated list of movies genres to retrieve. '
                            'Can be retrieved from the get_movies_genres command.',
                optional=True,
                type=list,
                example='-wg "Science Fiction,Fantasy"',
                converter=lambda genres: genres.split(',')
            ),
            Argument(
                name=['without_genres', 'wog'],
                description='Comma-separated list of movies genres to not retrieve. '
                            'Can be retrieved from the get_movies_genres command.',
                optional=True,
                type=list,
                example='-wog "Science Fiction,Fantasy"',
                converter=lambda genres: genres.split(',')
            ),
            Argument(
                name=['before_runtime', 'br'],
                description='Movies that their duration is no longer than the specific runtime. (minutes)',
                optional=True,
                type=int,
                example='-br "120"',
            ),
            Argument(
                name=['after_runtime', 'ar'],
                description='Movies that their duration is longer than the specific runtime. (minutes)',
                optional=True,
                type=int,
                example='-ar "120"',
            ),
            Flag(
                name=['not_released', 'nr'],
                description='Bring movies that were still not released.'
            ),
        ]
    )
    def discover_movies_command(
        self,
        update: Update,
        context: CallbackContext,
        limit: int,
        sort_by: str = None,
        before_date: str = None,
        after_date: str = None,
        with_genres: str = None,
        without_genres: str = None,
        before_runtime: str = None,
        after_runtime: str = None,
        not_released: bool = None
    ):
        return self._movie_conversation(update, context).discover_movies_command(
            limit=limit,
            sort_by=sort_by,
            before_date=before_date,
            after_date=after_date,
            with_genres=with_genres,
            without_genres=without_genres,
            before_runtime=before_runtime,
            after_runtime=after_runtime,
            not_released=not_released
        )

    def query_movie_overview(self, update: Update, context: CallbackContext):
        return self._movie_conversation(update, context).query_movie_overview()

    def display_movie_overview(self, update: Update, context: CallbackContext):
        return self._movie_conversation(update, context).display_movie_details()

    def query_movie_trailer(self, update: Update, context: CallbackContext):
        return self._movie_conversation(update, context).query_movie_trailer()

    def display_movie_trailer(self, update: Update, context: CallbackContext):
        return self._movie_conversation(update, context).display_movie_trailer()

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
                description='The maximum amount of tv-shows to return, maximum is 100.',
                validator=lambda x: 100 >= x > 0,
                optional=True,
                type=int,
                example='-n "game of thrones" -l "20"',
                default=50,
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
        context.bot.send_message(
            chat_id, text=f'Hang on while I am thinking, a bot needs to think too 🤓...')

        tv_shows_names = self._tv_shows_service().find_by_name(
            tv_show_name=name, limit=limit, sort_by=sort_by)
        if tv_shows_names:
            text = f'Found the following tv-shows for you 😀\n\n{tv_shows_names}'
        else:
            text = f'Could not find any tv-shows similar to the name "{name}" 😞'

        update.effective_message.reply_text(
            text=text, reply_to_message_id=update.message.message_id)

    @command(
        name='discover_tv_shows',
        description='Allows you to discover TV-shows by several options.',
        arguments=[
            Argument(
                name=['limit', 'l'],
                description='The maximum amount of tv-shows to return, maximum is 100.',
                validator=lambda x: 100 >= x > 0,
                optional=True,
                type=int,
                example='-l "80"',
                default=50,
            ),
            Selection(
                name=['sort-by', 's'],
                description='Sort by one of the allowed values',
                optional=True,
                type=str,
                example='-s "popularity"',
                default='popularity',
                allowed_values=['popularity', 'first_air_date', 'rating']
            ),
            Argument(
                name=['before_date', 'bd'],
                description='TV-shows that were released before '
                            'the specified date in the form of a date. "year-month-day"',
                optional=True,
                example='-bd "2014-09-13"',
                type=str
            ),
            Argument(
                name=['after_date', 'ad'],
                description='TV-shows that were released after '
                            'the specified date in the form of a date. "year-month-day"',
                optional=True,
                example='-ad "2014-09-13"',
                type=str
            ),
            Argument(
                name=['with_genres', 'wg'],
                description='TV-shows that are one of the genres that the get_tv_shows_genres command returns',
                optional=True,
                type=list,
                example='-wg "Science Fiction"',
                converter=lambda genres: genres.split(',')
            ),
            Argument(
                name=['without_genres', 'wog'],
                description='TV-shows that are not one of the genres that the get_tv_shows_genres returns.',
                optional=True,
                type=list,
                example='-wog "Science Fiction"',
                converter=lambda genres: genres.split(',')
            ),
            Argument(
                name=['before_runtime', 'br'],
                description='Filter and only include TV shows with an episode runtime '
                            'that is less than or equal to a value. (minutes)',
                optional=True,
                type=int,
                example='-br "120"',
            ),
            Argument(
                name=['after_runtime', 'ar'],
                description='Filter and only include TV shows with an episode runtime '
                            'that is greater than or equal to a value. (minutes)',
                optional=True,
                type=int,
                example='-ar "120"',
            ),
            Selection(
                name=['with_status', 'ws'],
                description='Filter TV shows by their status.',
                optional=True,
                type=str,
                example='-ws "Planned"',
                allowed_values=['Returning Series', 'Planned',
                                'In Production', 'Ended', 'Cancelled', 'Pilot']
            ),
            Flag(
                name=['not_released', 'nr'],
                description='Bring movies that were still not released.'
            ),
        ]
    )
    def discover_tv_shows_command(
        self,
        update: Update,
        context: CallbackContext,
        limit: int,
        sort_by: str = None,
        before_date: str = None,
        after_date: str = None,
        with_genres: str = None,
        without_genres: str = None,
        before_runtime: str = None,
        after_runtime: str = None,
        with_status: str = None,
        not_released: bool = None
    ):

        chat_id = update.message.chat_id
        context.bot.send_message(
            chat_id, text=f'Hang on while I am thinking, a bot needs to think too 🤓...')

        movie_names = self._tv_shows_service().discover(
            limit=limit,
            sort_by=sort_by,
            before_date=before_date,
            after_date=after_date,
            with_genres=with_genres,
            without_genres=without_genres,
            before_runtime=before_runtime,
            after_runtime=after_runtime,
            with_status=with_status,
            not_released=not_released
        )

        if movie_names:
            text = f'Found the following TV-shows for you 😀\n\n{movie_names}'
        else:
            text = 'Could not find any TV-shows for you 😞'

        update.effective_message.reply_text(
            text=text, reply_to_message_id=update.message.message_id)

    @command(name='get_movie_genres', description='Retrieves the available movies genres.')
    def get_movie_genres_command(self, update: Update, context: CallbackContext):

        chat_id = update.message.chat_id
        context.bot.send_message(
            chat_id, text=f'Hang on while I am thinking, a bot needs to think too 🤓...')

        movies_genres = self._movie_conversation().get_genres()
        if movies_genres:
            text = f'Movie Genres 😀\n\n{movies_genres}'
        else:
            text = f'Could not find any movie genres. 😞'

        update.effective_message.reply_text(
            text=text, reply_to_message_id=update.message.message_id)

    @command(name='get_tv_shows_genres', description='Retrieves the available TV-shows genres.')
    def get_tv_shows_genres_command(self, update: Update, context: CallbackContext):

        chat_id = update.message.chat_id
        context.bot.send_message(
            chat_id, text=f'Hang on while I am thinking, a bot needs to think too 🤓...')

        tv_shows_genres = self._tv_shows_service().get_genres()
        if tv_shows_genres:
            text = f'TV-shows Genres 😀\n\n{tv_shows_genres}'
        else:
            text = f'Could not find any TV-shows genres. 😞'

        update.effective_message.reply_text(
            text=text, reply_to_message_id=update.message.message_id)
