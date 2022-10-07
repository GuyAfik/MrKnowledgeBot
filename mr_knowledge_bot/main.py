
from mr_knowledge_bot.bot import Bot
from mr_knowledge_bot.bot.clients import MovieClient, TVShowsClient

if __name__ == '__main__':
    bot = Bot()
    bot.start()

    # c = TVShowsClient()
    # v = c.search(tv_show_name='breaking bad')
    # narcos_mexico_id = '80968'
    # d = c.get_videos(_id=narcos_mexico_id)
    # print()
    # a = MovieClient()
    # b = a.search(movie_name='interstellar')
    # interstellar_id = 157336
    # c = a.get_details(_id=interstellar_id)   # homepage, status, runtime
    # # c = TVShowsClient()
    # # d = c.discover(**{'primary_release_date.gte': '2022-09-27'})
    # print()