import logging

from telegram import Update
from telegram.ext import CallbackContext

from mr_knowledge_bot.bot.telegram.telegram_click.const import *
from mr_knowledge_bot.bot.telegram.telegram_click.util import escape_for_markdown

LOGGER = logging.getLogger(__name__)

# global list of all commands
COMMAND_LIST = []


class CommandTarget:
    """
    Values used to specify what command target (/command@target) to accept
    """
    # no target is specified (meaning there is no "@" in command)
    UNSPECIFIED = 1 << 0
    # directly targeted at this bot
    SELF = 1 << 1
    # directly targeted at another bot
    OTHER = 1 << 2
    # any of them
    ANY = UNSPECIFIED | SELF | OTHER


def generate_command_list(update: Update, context: CallbackContext, summary: bool = False) -> str:
    """
    :return: a Markdown styled text description of all available commands
    """
    if summary:
        return '\n'.join(
            [
                '/' + "|".join([escape_for_markdown(command_name) for command_name in command.get('names')])
                + ': ' + command.get('description') for command in COMMAND_LIST
            ]
        )

    else:
        commands_with_permission = list(
            filter(lambda x: x[KEY_PERMISSIONS] is None or x[KEY_PERMISSIONS].evaluate(update, context), COMMAND_LIST))
        commands_not_hidden = list(
            filter(lambda x: not x[KEY_HIDDEN] if isinstance(x[KEY_HIDDEN], bool)
            else not x[KEY_HIDDEN](update, context) if callable(x[KEY_HIDDEN])
            else True, commands_with_permission))
        sorted_commands = sorted(commands_not_hidden, key=lambda x: (x[KEY_NAMES][0].lower(), len(x[KEY_ARGUMENTS])))
        help_messages = list(map(lambda x: x[KEY_HELP_MESSAGE], sorted_commands))


        if len(COMMAND_LIST) <= 0:
            return "This bot does not have any commands."

        if len(commands_not_hidden) <= 0:
            return "You do not have permission to use commands."

        return "\n\n".join([
            *help_messages
        ])


