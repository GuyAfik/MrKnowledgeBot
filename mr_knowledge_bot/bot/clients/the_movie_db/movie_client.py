from abc import ABC
from mr_knowledge_bot.bot.clients.base_client import parse_http_response
from mr_knowledge_bot.bot.clients.the_movie_db.movie_db_base_client import TheMovieDBBaseClient, poll_movies_by_page


class TheMovieDBMovieClient(TheMovieDBBaseClient, ABC):

    @poll_movies_by_page
    @parse_http_response()
    def search(self, **kwargs):
        """
        Searches for movies with a specific name.

        Keyword Arguments:
            movie_name (str): the movie name. (required)
            page (int): which page should be queried. (optional)
        """
        if movie_name := kwargs.get('movie_name'):
            params = {'query': movie_name}
            if page := kwargs.get('page'):
                params['page'] = page
            return self.get(url='/search/movie', params=params)
        raise ValueError('The "movie_name" argument must be provided')

    @parse_http_response()
    def discover(self, **kwargs):
        """
        need to add docstring with all query parameters.
        """
        return self.get(url='/discover/movie', params=kwargs)

    @poll_movies_by_page
    @parse_http_response()
    def get_genres(self):
        return self.get(url='/genre/movie/list')
