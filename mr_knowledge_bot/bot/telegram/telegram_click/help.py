from typing import List

from mr_knowledge_bot.bot.telegram.telegram_click.argument import Argument
from mr_knowledge_bot.bot.telegram.telegram_click.const import ARG_NAMING_PREFIXES
from mr_knowledge_bot.bot.telegram.telegram_click.util import escape_for_markdown


def generate_help_message(names: [str], description: str, args: List[Argument]) -> str:
    """
    Generates a command usage description
    :param names: names of the command
    :param description: command description
    :param args: command argument list
    :return: help message
    """
    synopsis = generate_synopsis(names, args)

    flags = list(filter(lambda x: x.flag, args))
    flags = sorted(flags, key=lambda x: x.name)
    arguments = list(filter(lambda x: not x.flag, args))

    flags_description = generate_arguments_description(flags)
    arguments_description = generate_arguments_description(arguments)

    lines = [
        'Usage:',
        synopsis
    ]

    lines.extend([
        '\nDescription:',
        description
    ])

    if len(flags) > 0:
        lines.extend([
            "\nFlags:",
            flags_description
        ])

    if len(arguments) > 0:
        lines.extend([
            "\nArguments:",
            arguments_description
        ])

    if len(arguments) > 0 or len(flags) > 0:
        example = generate_command_example(names, arguments, flags)
        lines.extend([
            "\nExamples:",
            example
        ])

    return "\n".join(lines)


def generate_synopsis(names: [str], args: List[Argument]) -> str:
    """
    Generates the synopsis for a command
    :param names: command names
    :param args: arguments
    :return:
    """
    command_names = list(map(lambda x: f"/{escape_for_markdown(x)}", names))
    synopsis = command_names[0]
    # append command name aliases in round brackets
    if len(command_names) > 1:
        synopsis += " ({})".format(", ".join(command_names[1:]))
    # add hints about flags and arguments
    if len(args) > 0:
        if any(map(lambda x: x.flag, args)):
            synopsis += " [[FLAGS]]"
        if any(map(lambda x: not x.flag, args)):
            synopsis += " [[ARGS]]"

    return synopsis


def generate_arguments_description(args: List[Argument]) -> str:
    """
    Generates the description of all given arguments
    :param args: arguments
    :return: description
    """
    argument_lines = list(map(generate_argument_description, args))
    return "\n".join(argument_lines)


def generate_argument_description(arg: Argument) -> str:
    """
    Generates the usage text for an argument
    :param arg: the argument
    :return: usage text line
    """
    arg_prefix = next(iter(ARG_NAMING_PREFIXES))
    arg_names = list(map(lambda x: f"`{arg_prefix}{x}`", arg.names))

    message = "  " + ", ".join(arg_names)
    if not arg.flag:
        message += f"\t\t`{arg.type.__name__.upper()}`"
    message += f"\t\t{escape_for_markdown(arg.description)}"

    if arg.optional and not arg.flag:
        message += f'\t(default=`{escape_for_markdown(arg.default)}`)'
    return message


def generate_command_example(names: List[str], arguments: List[Argument], flags: List[Argument]) -> str:
    """
    Generates an example call of a command
    :param names: possible command names
    :param arguments: command arguments (without flags)
    :param flags: command flags
    :return: example call
    """
    arg_prefix = next(iter(ARG_NAMING_PREFIXES))
    argument_examples = list(map(lambda x: "{}".format(x.example), arguments))
    flag_examples = list(map(lambda x: "{}{}".format(arg_prefix, x.name), flags))
    return '\n'.join(
        [f'{num + 1}) `{"/" + names[0] + " " + argument_examples[num]}`'.strip()
         for num in range(len(argument_examples))]
    )

    # return "`/{} {}`".format(names[0], " ".join(flag_examples + argument_examples)).strip()