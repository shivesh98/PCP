import uuid
import datetime
from common.database import Database
from models.post import Post


class Chart(object):
    def __init__(self, name, author, title, description, author_id, _id=None):
        self.name = name
        self.author = author
        self.author_id = author_id
        self.title = title
        self.description = description
        self._id = uuid.uuid4().hex if _id is None else _id

    def new_post(self, title, content, date=datetime.datetime.utcnow()):
        post = Post(chart_id=self._id,
                    title=title,
                    content=content,
                    author=self.author,
                    created_date=date)
        post.save_to_mongo()

    def get_posts(self):
        return Post.from_chart(self._id)

    def save_to_mongo(self):
        Database.insert(collection="charts",
                        data=self.json())

    def json(self):
        return {
            'name' : self.name,
            'author': self.author,
            'author_id': self.author_id,
            'title': self.title,
            'description': self.description,
            '_id': self._id
        }

    @classmethod
    def from_mongo(cls, id):
        chart_data = Database.find_one(collection='charts',
                                      query={'_id': id})
        return cls(**chart_data)

    @classmethod
    def find_by_author_id(cls, author_id):
        charts = Database.find(collection='charts',
                              query={'author_id': author_id})
        return [cls(**chart) for chart in charts]
