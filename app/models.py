from app import db


class Booklist(db.Model):
	"""instances a book"""
	__tablename__ = 'bookslist'

	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(150), nullable=False)
	isbn = db.Column(db.String(10), nullable=False, unique=True)
	date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
	date_modified = db.Column(
		db.DateTime, default=db.func.current_timestamp(),
		onupdate=db.func.current_timestamp())

	def __init__(self, title, isbn):
		self.title = title
		self.isbn = isbn

	def save(self):
		db.session.add(self)
		db.session.commit()

	@staticmethod
	def get_all():
		return Booklist.query.all()

	def delete(self):
		db.session.delete(self)
		db.session.commit()

	def __repr__(self):
		return f"<Book {self.title}"
