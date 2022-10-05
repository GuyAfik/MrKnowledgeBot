from telegram.ext import CallbackContext, ConversationHandler
from abc import ABC
from mr_knowledge_bot.bot.conversations.telegram.conversation import Conversation
from telegram import Update, ReplyKeyboardMarkup, ParseMode, ReplyKeyboardRemove

from mr_knowledge_bot.bot.services import TVShowService


class TelegramTVShowConversation(Conversation, ABC):
    (
        query_tv_show_details_stage,
        display_tv_show_details_stage,
        query_tv_show_for_trailer_stage,
        display_tv_show_trailer_stage
    ) = range(4)

    def __init__(self, update: Update, context: CallbackContext):
        super().__init__(update, context)
        self._tv_shows_service = TVShowService.from_context(context=self.context)

    def find_tv_shows_by_name_command(self, tv_show_name, limit, sort_by):
        chat_id = self.update.message.chat_id
        self.context.bot.send_message(chat_id, text=self.hang_on_message)

        tv_shows = self._tv_shows_service.find_by_name(tv_show_name=tv_show_name, limit=limit, sort_by=sort_by)
        return self.display_tv_shows(tv_shows)

    def display_tv_shows(self, tv_shows):
        if tv_shows:
            self._context.user_data['tv_shows'] = tv_shows  # save the found movies for next stages in the conversation.
            tv_shows_names = '\n'.join([tv_show.name for tv_show in tv_shows])
            self._update.effective_message.reply_text(
                text=f'Found the following tv-shows for you 😀\n\n{tv_shows_names}',
                reply_to_message_id=self._update.message.message_id
            )
            next_stage = self.yes_or_no_tv_show_details()
        else:
            self._update.effective_message.reply_text(
                text=f'Could not find any tv-shows for you 😞',
                reply_to_message_id=self._update.message.message_id
            )
            next_stage = ConversationHandler.END

        return next_stage

    def yes_or_no_tv_show_details(self):
        self._context.bot.send_message(
            chat_id=self.get_chat_id(),
            text='Would you like to get a general information about one of the tv-shows 🎬?',
            reply_markup=self.get_yes_or_no_keyboard()
        )

        return self.query_tv_show_details_stage

    def choose_tv_show(self, answer):
        if answer == 'n':  # user does not want to proceed
            return None
        # user wants to proceed, e.g.: answer = 'y'
        return ReplyKeyboardMarkup.from_column(
            [tv_show.name for tv_show in self._tv_shows_service.tv_shows], resize_keyboard=True, one_time_keyboard=True
        )

    def query_tv_show_details(self):
        if tv_shows_to_choose := self.choose_tv_show(self._update.callback_query.data):
            text = 'Please choose a tv-show from the list to get its overview 🎬'
            self._context.bot.send_message(
                text=text, reply_markup=tv_shows_to_choose, chat_id=self.get_chat_id()
            )
            next_stage = self.display_tv_show_details_stage
        else:
            if self._context.user_data.get('repeat'):
                next_stage = ConversationHandler.END
                self._context.bot.edit_message_text(
                    text='Thank you! If you want to see additional commands, run /help',
                    chat_id=self.get_chat_id(),
                    message_id=self.get_message_id()
                )
                self._context.user_data['repeat'] = False
            else:
                # next_stage = self.yes_or_no_movie_trailer()
                next_stage = ConversationHandler.END

        return next_stage

    def display_tv_show_details(self):
        chosen_tv_show = self._update.message.text
        if tv_show := self._tv_shows_service.get_details(chosen_tv_show):
            text = ''
            if tv_show_overview := tv_show.overview:
                text = f'*{chosen_tv_show} - (Overview)*\n\n{tv_show_overview}'
            if tv_show_homepage := tv_show.homepage:
                text = f'{text}\n\n*Homepage:* {tv_show_homepage}'
            if tv_show_status := tv_show.status:
                text = f'{text}\n\n*Status:* {tv_show_status}'
            if tv_show_release_date := tv_show.release_date:
                text = f'{text}\n\n*Release date:* {tv_show_release_date}'
            if tv_show_seasons := tv_show.seasons:
                text = f'{text}\n\n*Number Of Seasons:* {len(tv_show_seasons)}'
            if tv_show_number_of_episodes := tv_show.number_of_episodes:
                text = f'{text}\n\n*Number Of Episodes:* {tv_show_number_of_episodes}'

            self._update.effective_message.reply_text(
                text=text,
                reply_to_message_id=self._update.message.message_id,
                reply_markup=ReplyKeyboardRemove(),
                parse_mode=ParseMode.MARKDOWN
            )

            # next_stage = self.yes_or_no_movie_trailer()
            next_stage = ConversationHandler.END
        else:
            self._update.effective_message.reply_text(
                text='I could not understand which tv-show you meant 🤔, please choose again from the list.',
                reply_to_message_id=self._update.message.message_id
            )
            next_stage = self.display_tv_show_details_stage

        return next_stage