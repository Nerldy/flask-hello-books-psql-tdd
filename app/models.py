from app import db
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
from flask import current_app


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


class APIUser(db.Model):
	"""defines users"""
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(50), index=True, unique=True, nullable=False)
	email = db.Column(db.String(100), index=True, unique=True, nullable=False)
	password_hash = db.Column(db.String, nullable=False)
	is_admin = db.Column(db.Boolean, default=False)
	date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
	date_modified = db.Column(
		db.DateTime, default=db.func.current_timestamp(),
		onupdate=db.func.current_timestamp())

	@property
	def password(self):
		"""
		Prevent password from being accessed
		"""
		raise AttributeError('password is not a readable attribute.')

	@password.setter
	def password(self, password):
		"""
		Set password to a hashed password
		"""
		self.password_hash = generate_password_hash(password)

	def verify_password(self, password):
		"""
		Check if hashed password matches actual password
		"""
		return check_password_hash(self.password_hash, password)

	def save(self):
		"""
		save user to database
		"""
		db.session.add(self)
		db.session.commit()

	def __repr__(self):
		return f'<user: {self.username}>'

	def generate_token(self, user_id):
		""" Generates the access token"""

		try:
			# set up a payload with an expiration time
			payload = {
				'exp': datetime.utcnow() + timedelta(minutes=30),
				'iat': datetime.utcnow(),
				'sub': user_id
			}
			# create the byte string token using the payload and the SECRET key
			jwt_string = jwt.encode(
				payload=payload,
				key=current_app.config.get('SECRET'),
				algorithm='HS256'
			)

			return jwt_string

		except Exception as e:
			# return an error in string format if an exception occurs
			return str(e)

	@staticmethod
	def decode_token(token):
		"""Decodes the access token from the Authorization header."""
		try:
			# try to decode the token using our SECRET variable
			payload = jwt.decode(token, current_app.config.get('SECRET'))
			return payload['sub']
		except jwt.ExpiredSignatureError:
			# the token is expired, return an error string
			return "Expired token. Please login to get a new token"
		except jwt.InvalidTokenError:
			# the token is invalid, return an error string
			return "Invalid token. Please register or login"
