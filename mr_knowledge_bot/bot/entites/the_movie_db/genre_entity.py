

class GenreEntity:
    def __init__(self, _id, name):
        self.id = _id
        self.name = name

    @classmethod
    def from_response(cls, response):
        return cls(_id=response.get('id'), name=response.get('name'))
