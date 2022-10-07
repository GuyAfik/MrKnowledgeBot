
from mr_knowledge_bot.bot import Bot
from mr_knowledge_bot.bot.clients import MovieClient, TVShowsClient
from mr_knowledge_bot.bot.services.youtube_downloader_service import YouTubeVideoDownloader

if __name__ == '__main__':
    bot = Bot()
    bot.start()

    with YouTubeVideoDownloader(url='https://www.youtube.com/watch?v=9K7c0jXkaGc') as f:
        print()

    # c = TVShowsClient()
    # v = c.search(tv_show_name='game of thrones')
    # house_of_dragon_id = '94997'
    #
    # d = c.get_videos(_id=house_of_dragon_id)
    #
    # # d = c.get_details(_id=game_of_thrones_id)
    #
    # print()
    # a = MovieClient()
    # b = a.search(movie_name='interstellar')
    # interstellar_id = 157336
    # c = a.get_details(_id=interstellar_id)   # homepage, status, runtime
    # # c = TVShowsClient()
    # # d = c.discover(**{'primary_release_date.gte': '2022-09-27'})
    # print()