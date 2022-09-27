
from mr_knowledge_bot.bot import Bot
from mr_knowledge_bot.bot.clients import MovieClient


if __name__ == '__main__':
    bot = Bot()
    bot.start()
    # a = MovieClient()
    # b = a.discover(**{'release_date.gte': '2025-09-27'})
    # print()