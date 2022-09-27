
from mr_knowledge_bot.bot import Bot
from mr_knowledge_bot.bot.clients import MovieClient, TVShowsClient


if __name__ == '__main__':
    # bot = Bot()
    # bot.start()

    a = MovieClient()
    b = a.discover(**{'primary_release_date.gte': '2022-09-27'})
    c = TVShowsClient()
    d = c.discover(**{'primary_release_date.gte': '2022-09-27'})
    print()