from abc import ABC
from mr_knowledge_bot.bot.base_bot import BaseBot
from telegram.ext import CommandHandler, CallbackContext, MessageHandler, Updater, Filters, CallbackQueryHandler, ConversationHandler
from telegram import Update, ParseMode
from mr_knowledge_bot.bot.telegram.telegram_click.decorator import command
from mr_knowledge_bot.bot.telegram.telegram_click.argument import Argument, Selection, Flag
from mr_knowledge_bot.bot.logic import MovieLogic, TVShowLogic
from mr_knowledge_bot.bot.telegram.telegram_click import generate_command_list
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineQuery, ReplyKeyboardMarkup, KeyboardButton


class TelegramBot(BaseBot, ABC):

    commands_phase, help_phase, query_movie_for_overview, display_movie_overview_stage = range(4)

    def __init__(self, token=None):
        super().__init__(token)
        self._updater = Updater(token=self.token, use_context=True)
        self._movie_commands_logic = MovieLogic
        self._tv_shows_commands_logic = TVShowLogic

        find_movie_by_name_conversation_handler = ConversationHandler(
            entry_points=[
                CommandHandler(command='find_movies_by_name', callback=self.find_movies_by_name_command),
            ],
            states={
                self.query_movie_for_overview: [
                    CallbackQueryHandler(callback=self.query_movie_overview)
                ],
                self.display_movie_overview_stage: [
                    MessageHandler(filters=Filters.regex('^(?!.*exit).*$'), callback=self.display_movie_overview)
                ]
            },
            fallbacks=[MessageHandler(filters=Filters.regex('^exit$'), callback=self.cancel_conversation)],
            allow_reentry=True
        )

        handler_groups = {
            0: [
                CommandHandler(command='help', callback=self.help_command),
                find_movie_by_name_conversation_handler,
                CommandHandler(command='find_tv_shows_by_name', callback=self.find_tv_shows_by_name_command),
                CommandHandler(command='discover_movies', callback=self.discover_movies_command),
                CommandHandler(command='discover_tv_shows', callback=self.discover_tv_shows_command),
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

    @command(name=['help'], description='List the commands supported by the MrKnowledgeBot')
    def help_command(self, update: Update, context: CallbackContext):
        self.send_available_commands(update, context)

    @staticmethod
    def send_available_commands(update: Update, context: CallbackContext):
        bot = context.bot
        chat_id = update.effective_message.chat_id

        user_info = update.message.from_user
        first_name = user_info.first_name
        last_name = user_info.last_name

        text = f'Hello {first_name} {last_name}! Here are the available commands 😎' \
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
        chat_id = update.message.chat_id
        context.bot.send_message(chat_id, text=f'Hang on while I am thinking, a bot needs to think too 🤓...')

        movies = self._movie_commands_logic().find_by_name(movie_name=name, limit=limit, sort_by=sort_by)
        if movies:
            context.user_data['movies'] = movies
            movie_names = '\n'.join([movie.name for movie in movies])
            text = f'Found the following movies for you 😀\n\n{movie_names}'
        else:
            text = f'Could not find any movies similar to the name "{name}" 😞'

        update.effective_message.reply_text(text=text, reply_to_message_id=update.message.message_id)

        keyboard = self._movie_commands_logic.get_overview_keyboard()
        context.bot.send_message(
            chat_id=chat_id, text='Would you like to see an overview of one of the movies?', reply_markup=keyboard
        )

        return self.query_movie_for_overview

    def query_movie_overview(self, update: Update, context: CallbackContext):
        movie_commands_logic = self._movie_commands_logic.from_context(context)
        movies_to_choose = movie_commands_logic.choose_movie(update.callback_query.data)
        if movies_to_choose:
            text = 'Please choose a movie from the list to get its overview.'
            next_stage = self.display_movie_overview_stage
        else:
            text = 'I hope you to see you around again! 😀'
            next_stage = ConversationHandler.END

        context.bot.send_message(chat_id=update.callback_query.message.chat_id, text=text, reply_markup=movies_to_choose)
        return next_stage

    def display_movie_overview(self, update: Update, context: CallbackContext):
        movie_commands_logic = self._movie_commands_logic.from_context(context)
        chosen_movie_name = update.message.text

        movie_overview = movie_commands_logic.get_movie_overview(chosen_movie_name)
        if movie_overview:
            text = f'{chosen_movie_name} - (Overview):\n\n{movie_overview}'
            next_phase = ConversationHandler.END
        else:
            text = 'I could not understand which movie you meant 🤔, please choose again from the list.'
            next_phase = self.display_movie_overview_stage

        update.effective_message.reply_text(text=text, reply_to_message_id=update.message.message_id)
        return next_phase

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
        context.bot.send_message(chat_id, text=f'Hang on while I am thinking, a bot needs to think too 🤓...')

        tv_shows_names = self._tv_shows_commands_logic().find_by_name(tv_show_name=name, limit=limit, sort_by=sort_by)
        if tv_shows_names:
            text = f'Found the following tv-shows for you 😀\n\n{tv_shows_names}'
        else:
            text = f'Could not find any tv-shows similar to the name "{name}" 😞'

        update.effective_message.reply_text(text=text, reply_to_message_id=update.message.message_id)

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
        chat_id = update.message.chat_id
        context.bot.send_message(chat_id, text=f'Hang on while I am thinking, a bot needs to think too 🤓...')

        movie_names = self._movie_commands_logic().discover(
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

        if movie_names:
            text = f'Found the following movies for you 😀\n\n{movie_names}'
        else:
            text = 'Could not find any movies for you 😞'

        update.effective_message.reply_text(text=text, reply_to_message_id=update.message.message_id)

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
        context.bot.send_message(chat_id, text=f'Hang on while I am thinking, a bot needs to think too 🤓...')

        movie_names = self._tv_shows_commands_logic().discover(
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

        update.effective_message.reply_text(text=text, reply_to_message_id=update.message.message_id)

    @command(name='get_movie_genres', description='Retrieves the available movies genres.')
    def get_movie_genres_command(self, update: Update, context: CallbackContext):

        chat_id = update.message.chat_id
        context.bot.send_message(chat_id, text=f'Hang on while I am thinking, a bot needs to think too 🤓...')

        movies_genres = self._movie_commands_logic().get_genres()
        if movies_genres:
            text = f'Movie Genres 😀\n\n{movies_genres}'
        else:
            text = f'Could not find any movie genres. 😞'

        update.effective_message.reply_text(text=text, reply_to_message_id=update.message.message_id)

    @command(name='get_tv_shows_genres', description='Retrieves the available TV-shows genres.')
    def get_tv_shows_genres_command(self, update: Update, context: CallbackContext):

        chat_id = update.message.chat_id
        context.bot.send_message(chat_id, text=f'Hang on while I am thinking, a bot needs to think too 🤓...')

        tv_shows_genres = self._tv_shows_commands_logic().get_genres()
        if tv_shows_genres:
            text = f'TV-shows Genres 😀\n\n{tv_shows_genres}'
        else:
            text = f'Could not find any TV-shows genres. 😞'

        update.effective_message.reply_text(text=text, reply_to_message_id=update.message.message_id)
