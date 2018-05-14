from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
from cerberus import Validator
import re

# local import
from instance.config import app_config

# initialize sql-alchemy
db = SQLAlchemy()


# useful functions
def format_inputs(word):
	"""
	formats input string
	:param word:
	:return: string
	"""
	json_input = word.lower().strip()
	split_input = re.sub(' +', " ", json_input)
	return "".join(split_input)


# schemas

book_schema = {
	'title': {
		'type': 'string',
		'required': True,
		'empty': False
	},
	'isbn': {
		'type': "string",
		'required': True
	}
}

validate_book_schema = Validator(book_schema)


def create_app(config_name):
	from app.models import Booklist

	app = Flask(__name__, instance_relative_config=True)
	app.config.from_object(app_config[config_name])
	app.config.from_pyfile('config.py')
	app.url_map.strict_slashes = False
	app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
	db.init_app(app)

	@app.errorhandler(404)
	def page_not_found(e):
		return jsonify({'error': 'not found'}), 404

	@app.errorhandler(400)
	def bad_request(e):
		return jsonify({"error": 'bad request'}), 400

	@app.route('/api/v2/books')
	def api_get_all_books():
		"""
		:return: book list, 200
		"""
		all_books = Booklist.get_all()
		books_result = []

		for book in all_books:
			book_obj = {
				'id': book.id,
				'title': book.title,
				'isbn': book.isbn,
				'dte_created': book.date_created,
				'date_modified': book.date_modified
			}
			books_result.append(book_obj)
		return jsonify({'books': books_result})

	@app.route('/api/v2/books', methods=['POST'])
	def api_create_book():
		req_data = request.get_json()

		if not req_data:
			"""abort if no JSON object detected"""
			abort(400)

		if validate_book_schema.validate(req_data):
			try:
				title = format_inputs(req_data.get('title'))
				isbn = format_inputs(req_data.get('isbn'))

				if len(isbn) != 10:
					return jsonify({'error': "isbn length must be 10"}), 400

				if isbn.isnumeric():
					new_book = Booklist(title=title, isbn=isbn)
					new_book.save()

					book_json = {
						'id': new_book.id,
						'title': new_book.title,
						'isbn': new_book.isbn,
						'date_created': new_book.date_created
					}

					return jsonify({"book_created": book_json}), 201

				return jsonify({'error': "isbn must only include numbers"}), 400
			except:
				abort(400)

		return jsonify({'error': validate_book_schema.errors}), 400

	@app.route('/api/v2/books/<int:id>')
	def api_get_book_with_id(id):

		book = Booklist.query.filter(Booklist.id == id).first()

		if not book:
			abort(404)

		return jsonify({
			'id': book.id,
			'title': book.title,
			'isbn': book.isbn,
			'date_created': book.date_created,
			'date_modified': book.date_modified
		})

	return app
