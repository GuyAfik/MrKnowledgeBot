import logging
from abc import ABC
from mr_knowledge_bot.bot.base_bot import BaseBot
from telegram.ext import CommandHandler, CallbackContext, MessageHandler, Updater, Filters, CallbackQueryHandler, ConversationHandler
from telegram import Update, ParseMode, ReplyKeyboardRemove
from mr_knowledge_bot.bot.telegram.telegram_click.decorator import command
from mr_knowledge_bot.bot.telegram.telegram_click.argument import Argument, Selection, Flag
from mr_knowledge_bot.bot.conversations import MovieConversation, TVShowConversation
from mr_knowledge_bot.bot.telegram.telegram_click import generate_command_list


logger = logging.getLogger(__name__)


def error_handler(func):
    def wrapper(self, update: Update, context: CallbackContext, *args, **kwargs):
        try:
            return func(self, update, context, *args, **kwargs)
        except Exception as e:
            logger.error(f'Error:\n{e}')
            message = update.message or update.effective_message or update.callback_query.message
            first_name = message.from_user.first_name
            last_name = message.from_user.last_name
            chat_id = message.chat_id
            context.bot.send_message(
                chat_id=chat_id,
                text=f'Hi {first_name} {last_name}, sorry, an error occurred '
                     f'during my thinking process, my apologies. Feel free to try again.'
            )
            return self.cancel_conversation(update, context)
    return wrapper


class TelegramBot(BaseBot, ABC):

    def __init__(self, token=None):
        super().__init__(token)
        self._updater = Updater(token=self.token, use_context=True)
        self._movie_conversation = MovieConversation
        self._tv_show_conversation = TVShowConversation

        movies_conversation_handler = ConversationHandler(
            entry_points=[
                CommandHandler(command='find_movies_by_name', callback=self.find_movies_by_name_command),
                CommandHandler(command='discover_movies', callback=self.discover_movies_command),
            ],
            states={
                self._movie_conversation.query_movie_details_stage: [
                    CallbackQueryHandler(callback=self.query_movie_details)
                ],
                self._movie_conversation.display_movie_details_stage: [
                    MessageHandler(filters=Filters.regex('^(?!.*exit).*$'), callback=self.display_movie_details)
                ],
                self._movie_conversation.query_movie_for_trailer_stage: [
                    CallbackQueryHandler(callback=self.query_movie_trailer)
                ],
                self._movie_conversation.display_movie_trailer_stage: [
                    MessageHandler(filters=Filters.regex('^(?!.*exit).*$'), callback=self.display_movie_trailer)
                ]
            },
            fallbacks=[MessageHandler(filters=Filters.regex('^exit$'), callback=self.cancel_conversation)],
            allow_reentry=True
        )

        tv_show_conversation_handler = ConversationHandler(
            entry_points=[
                CommandHandler(command='find_tv_shows_by_name', callback=self.find_tv_shows_by_name_command),
                CommandHandler(command='discover_tv_shows', callback=self.discover_tv_shows_command)
            ],
            states={
                self._tv_show_conversation.query_tv_show_details_stage: [
                    CallbackQueryHandler(callback=self.query_tv_show_details)
                ],
                self._tv_show_conversation.display_tv_show_details_stage: [
                    MessageHandler(filters=Filters.regex('^(?!.*exit).*$'), callback=self.display_tv_show_details)
                ],
                self._tv_show_conversation.query_tv_show_season_stage: [
                    CallbackQueryHandler(callback=self.query_tv_show_season)
                ],
                self._tv_show_conversation.display_tv_show_season_stage: [
                    MessageHandler(filters=Filters.regex('^(?!.*exit).*$'), callback=self.display_tv_show_season)
                ],
                self._tv_show_conversation.display_tv_show_trailer_stage: [
                    CallbackQueryHandler(callback=self.display_tv_show_trailer)
                ]
            },
            fallbacks=[MessageHandler(filters=Filters.regex('^exit$'), callback=self.cancel_conversation)]
        )

        handler_groups = {
            0: [
                CommandHandler(command='help', callback=self.help_command),
                movies_conversation_handler,
                tv_show_conversation_handler,
                CommandHandler(command='get_movie_genres', callback=self.get_movie_genres_command),
                CommandHandler(command='get_tv_shows_genres', callback=self.get_tv_shows_genres_command)
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

        if update.callback_query:
            message = update.callback_query.message
        else:
            message = update.message

        user_info = message.from_user
        first_name = user_info.first_name
        last_name = user_info.last_name

        text = f'Hello {first_name} {last_name}! Here are the available conversations 😎' \
               f'\n\n{generate_command_list(update, context, summary=True)}\n\n' \
               f'For more information please refer to https://github.com/GuyAfik/MrKnowledgeBot/blob/master/README.md'
        bot.send_message(chat_id, text, parse_mode=ParseMode.MARKDOWN, reply_markup=ReplyKeyboardRemove())

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
    @error_handler
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
    @error_handler
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

    @error_handler
    def query_movie_details(self, update: Update, context: CallbackContext):
        return self._movie_conversation(update, context).query_movie_details()

    @error_handler
    def display_movie_details(self, update: Update, context: CallbackContext):
        return self._movie_conversation(update, context).display_movie_details()

    @error_handler
    def query_movie_trailer(self, update: Update, context: CallbackContext):
        return self._movie_conversation(update, context).query_movie_trailer()

    @error_handler
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
    @error_handler
    def find_tv_shows_by_name_command(
        self, update: Update, context: CallbackContext, name: str, limit: int, sort_by: str
    ):
        return self._tv_show_conversation(update, context).find_tv_shows_by_name_command(
            tv_show_name=name, limit=limit, sort_by=sort_by
        )

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
                allowed_values=['Returning Series', 'Planned', 'In Production', 'Ended', 'Cancelled', 'Pilot']
            ),
            Flag(
                name=['not_released', 'nr'],
                description='Bring movies that were still not released.'
            ),
        ]
    )
    @error_handler
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
        return self._tv_show_conversation(update, context).discover_tv_shows_command(
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

    @error_handler
    def query_tv_show_details(self, update: Update, context: CallbackContext):
        return self._tv_show_conversation(update, context).query_tv_show_details()

    @error_handler
    def display_tv_show_details(self, update: Update, context: CallbackContext):
        return self._tv_show_conversation(update, context).display_tv_show_details()

    @error_handler
    def query_tv_show_season(self, update: Update, context: CallbackContext):
        return self._tv_show_conversation(update, context).query_specific_tv_show_season()

    @error_handler
    def display_tv_show_season(self, update: Update, context: CallbackContext):
        return self._tv_show_conversation(update, context).display_tv_show_season()

    @error_handler
    def display_tv_show_trailer(self, update: Update, context: CallbackContext):
        return self._tv_show_conversation(update, context).display_tv_show_trailer()

    @command(name='get_movie_genres', description='Retrieves the available movies genres.')
    @error_handler
    def get_movie_genres_command(self, update: Update, context: CallbackContext):
        return self._movie_conversation(update, context).get_genres()

    @command(name='get_tv_shows_genres', description='Retrieves the available TV-shows genres.')
    @error_handler
    def get_tv_shows_genres_command(self, update: Update, context: CallbackContext):
        return self._tv_show_conversation(update, context).get_genres()
