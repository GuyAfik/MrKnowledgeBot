
from mr_knowledge_bot.bot import Bot
from mr_knowledge_bot.bot.clients import MovieClient


if __name__ == '__main__':
    # bot = Bot()
    # bot.start()
    a = MovieClient()
    b = a.discover(**{'primary_release_date.lte': '2021-06-01'})
    print()