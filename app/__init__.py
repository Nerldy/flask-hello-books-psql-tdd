from flask import Flask, jsonify, request, abort, make_response
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

update_book_schema = {
	'title': {
		'type': 'string',
		'required': True,
		'empty': False
	}
}

pagination_schema = {
	'limit': {
		'type': 'string',
		'required': True
	},
	'page_num': {
		'type': 'string',
		'required': True
	}
}

# schema validations
validate_book_schema = Validator(book_schema)
validate_update_book_schema = Validator(update_book_schema)
validate_pagination_schema = Validator(pagination_schema)


def create_app(config_name):
	from app.models import Booklist
	from app.helpers_funcs import token_required, check_admin

	app = Flask(__name__, instance_relative_config=True)
	app.config.from_object(app_config[config_name])
	app.config.from_pyfile('config.py')
	app.url_map.strict_slashes = False
	app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
	db.init_app(app)

	@app.errorhandler(403)
	def forbidden(e):
		return jsonify({'error': 'forbidden'}), 403

	@app.errorhandler(404)
	def page_not_found(e):
		return jsonify({'error': 'not found'}), 404

	@app.errorhandler(400)
	def bad_request(e):
		return jsonify({"error": 'bad request'}), 400

	@app.errorhandler(500)
	def internal_server_error(e):
		return jsonify({'error': 'internal server error'}), 500

	@app.route('/api/v2/books')
	# @token_required
	def api_get_all_books():
		"""
		:return: book list, 200
		"""
		all_books = Booklist.get_all()
		books_result = []

		req_args = request.args

		# check if pagination args are provided
		if req_args:
			if validate_pagination_schema.validate(req_args):
				try:
					page_limit = int(request.args.get('limit'))
					page_number = int(request.args.get('page_num'))

					book_pagination = Booklist.query.paginate(
						per_page=page_limit,
						page=page_number,
						error_out=True
					)

					for book in book_pagination.items:
						book_obj = {
							'id': book.id,
							'title': book.title,
							'isbn': book.isbn,
							'date_created': book.date_created,
							'date_modified': book.date_modified
						}
						books_result.append(book_obj)

					return make_response(
						jsonify({
							'current_page': book_pagination.page,
							'pages': book_pagination.pages,
							"books": books_result
						})
					)
				except Exception as e:
					return make_response(
						jsonify(
							{
								'error': str(e)
							}
						)
					), 400

			return make_response(jsonify({'error': validate_pagination_schema.errors})), 400

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
	@token_required
	def api_create_book(current_user):

		check_admin(current_user)

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
				return jsonify({'error': f"book with ISBN {req_data.get('isbn')} already exists"}), 400

		return jsonify({'error': validate_book_schema.errors}), 400

	@app.route('/api/v2/books/<int:id>')
	@token_required
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

	@app.route('/api/v2/books/<int:id>', methods=['PUT'])
	@token_required
	def api_update_book(current_user, id):

		check_admin(current_user)

		req_data = request.get_json()
		book = Booklist.query.filter(Booklist.id == id).first()

		if not req_data:
			"""abort if no JSON object detected"""
			abort(400)

		if not book:
			abort(404)

		if validate_update_book_schema.validate(req_data):
			title = format_inputs(req_data.get('title'))
			book.title = title
			book.save()

			book_json = {
				'id': book.id,
				'title': book.title,
				'isbn': book.isbn,
				'date_created': book.date_created,
				'date_modified': book.date_modified
			}

			return jsonify({"book_updated": book_json}), 201

		return jsonify({'error': validate_update_book_schema.errors})

	@app.route('/api/v2/books/<int:id>', methods=['DELETE'])
	@token_required
	def api_delete_book(current_user, id):

		check_admin(current_user)

		book = Booklist.query.filter(Booklist.id == id).first()

		if not book:
			abort(404)

		book.delete()
		return jsonify({'message': f'Book with ID {book.id} deleted'})

	# authentication blueprint
	from .auth import auth_blueprint
	app.register_blueprint(auth_blueprint)

	return app
