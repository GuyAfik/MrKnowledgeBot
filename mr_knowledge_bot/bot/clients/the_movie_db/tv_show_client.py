from abc import ABC
from mr_knowledge_bot.bot.clients.base_client import parse_http_response
from mr_knowledge_bot.bot.clients.the_movie_db.movie_db_base_client import TheMovieDBBaseClient, poll_by_page_and_limit
from mr_knowledge_bot.bot.entites.the_movie_db.tv_show_entity import TheMovieDBTVShowEntity


class TheMovieDBTVShowsClient(TheMovieDBBaseClient, ABC):

    tv_show_entity = TheMovieDBTVShowEntity

    @poll_by_page_and_limit()
    @parse_http_response(response_type='json', keys=['results'])
    def search(self, **kwargs):
        """
        Searches for movies with a specific name.

        Keyword Arguments:
            tv_show_name (str): the TV-show name. (required)
            page (int): which page should be queried. (optional)
        """
        if tv_show_name := kwargs.get('tv_show_name'):
            params = {'query': tv_show_name}
            if page := kwargs.get('page'):
                params['page'] = page
            return self.get(url='/search/tv', params=params)
        raise ValueError('The "tv_show_name" argument must be provided')

    @poll_by_page_and_limit()
    @parse_http_response(_class_type=tv_show_entity)
    def discover(self, **kwargs):
        return self.get(url='/discover/tv', params=kwargs)

    @parse_http_response(response_type='json')
    def get_genres(self):
        return self.get(url='/genre/tv/list')
