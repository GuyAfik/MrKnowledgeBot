from mr_knowledge_bot.bot.entites.the_movie_db.base import TheMovieDBBaseEntity


class VideoEntity(TheMovieDBBaseEntity):

    def __init__(self, _id, name, _type, key, published_at, site, is_official):
        super().__init__(_id, name)
        self.type = _type.lower()
        self.key = key
        self.published_at = published_at
        self.site = site.lower()
        self.is_official = is_official

    @classmethod
    def from_response(cls, response):
        results = response.get('results') or []
        return [
            cls(
                name=result.get('name'),
                _id=result.get('id'),
                _type=result.get('type'),
                key=result.get('key'),
                published_at=result.get('published_at'),
                site=result.get('site'),
                is_official=result.get('official')
            ) for result in results
        ]

    def __str__(self):
        if self.type in ('trailer', 'teaser') and self.site == 'youtube':
            return f'https://www.youtube.com/watch?v={self.key}'
        return ''



