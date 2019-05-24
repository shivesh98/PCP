import uuid
from common.database import Database
import datetime


class Post(object):
	"""docstring for Post"""
	def __init__(self, name, chart_id, title, content, author, created_date=datetime.datetime.utcnow(), _id=None):
		self.name = name
		self.chart_id = chart_id
		self.title = title
		self.content = content
		self.author = author
		self.created_date = created_date
		if _id is None:
			self._id = uuid.uuid4().hex
		else:
			self._id = _id

	def save_to_mongo(self):
		Database.insert(collection='posts',
					data=self.json())

	def  json(self):
		return {
			'name': self.name,
			'chart_id': self.chart_id,
			'title': self.title,
			'content': self.content,
			'author': self.author,
			'created_date': self.created_date,
			'_id': self._id
		}

	@classmethod
	def from_mongo(cls, id):
		post_data = Database.find_one(collection='posts',
									query={'_id': _id})
		return cls(**post_data)

	@staticmethod
	def from_chart(id):
		return [post for post in Database.find(collection='posts',
												query={'chart_id': id})]