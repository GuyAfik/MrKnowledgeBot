from mr_knowledge_bot.bot.entites.the_movie_db.base import TheMovieDBBaseEntity


class VideoEntity(TheMovieDBBaseEntity):

    def __init__(self, _id, name, _type, key, published_at, site, is_official):
        super().__init__(_id, name)
        self.type = _type
        self.key = key
        self.published_at = published_at
        self.site = site
        self.is_official = is_official

    @classmethod
    def from_response(cls, response):
        return cls(
            name=response.get('name'),
            _id=response.get('id'),
            _type=response.get('type'),
            key=response.get('key'),
            published_at=response.get('published_at'),
            site=response.get('site'),
            is_official=response.get('official')
        )

    def __str__(self):
        if self.type == 'Trailer' and self.is_official:
            platform = f'https://www.youtube.com/watch?v=' if self.site.lower() == 'youtube' else 'https://vimeo.com/'
            return f'{platform}{self.key}'
        return ''
