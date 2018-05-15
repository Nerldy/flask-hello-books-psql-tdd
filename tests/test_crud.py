import unittest
import os
import json
from app import create_app, db
from flask_testing import TestCase


class BooklistTestCase(unittest.TestCase):

	def setUp(self):
		self.app = create_app(config_name="testing")
		self.client = self.app.test_client
		self.bookslist = {"title": 'Hello Books', "isbn": "0036593325"}

		with self.app.app_context():
			# create all tables
			db.create_all()

	def tearDown(self):
		"""teardown all initialized variables."""
		with self.app.app_context():
			# drop all tables
			db.session.remove()
			db.drop_all()

	def test_api_booklist_creation(self):
		"""test api can POST a book"""
		res = self.client().post(
			'/api/v2/books',
			data=json.dumps(self.bookslist),
			content_type='application/json')
		self.assertEqual(res.status_code, 201)
		self.assertIn('book_created', str(res.data))

	def test_api_book_create_no_json_error(self):
		"""test API returns 400 error"""
		book = ""
		res = self.client().post(
			'/api/v2/books',
			data=json.dumps(book),
			content_type='application/json'
		)
		self.assertEqual(res.status_code, 400)
		self.assertIn('bad request', str(res.data))

	def test_api_create_book_validation_error(self):
		"""test API validation error"""
		book = {
			'title': "bool"
		}
		res = self.client().post(
			'/api/v2/books',
			data=json.dumps(book),
			content_type='application/json'
		)
		self.assertEqual(res.status_code, 400)
		self.assertIn('error', str(res.data))

	def test_create_book_isbn_error(self):
		"""test API can't create book if ISBN length is not 10 digits"""
		book = {
			'title': "bool",
			"isbn": "56951478"
		}
		res = self.client().post(
			'/api/v2/books',
			data=json.dumps(book),
			content_type='application/json'
		)
		self.assertEqual(res.status_code, 400)
		self.assertIn('isbn length must be 10', str(res.data))

	def test_create_book_isbn_must_be_nubers(self):
		"""test API can't create book if ISBN are only numbers"""
		book = {
			'title': "bool",
			"isbn": "845623369r"
		}
		res = self.client().post(
			'/api/v2/books',
			data=json.dumps(book),
			content_type='application/json'
		)
		self.assertEqual(res.status_code, 400)
		self.assertIn('isbn must only include numbers', str(res.data))

	def test_create_book_isbn_exists(self):
		"""test API can't create book if ISBN are only numbers"""
		book = {
			'title': "bool",
			"isbn": "5698874586"
		}

		book2 = {
			'title': "bool",
			"isbn": "5698874586"
		}

		res = self.client().post(
			'/api/v2/books',
			data=json.dumps(book),
			content_type='application/json'
		)
		self.assertEqual(res.status_code, 201)
		self.assertIn('book_created', str(res.data))
		res = self.client().post(
			'/api/v2/books',
			data=json.dumps(book2),
			content_type='application/json'
		)
		self.assertIn('already exists', str(res.data))

	def test_api_gets_all_books(self):
		"""test api GET all books"""
		res = self.client().post(
			'/api/v2/books',
			data=json.dumps(self.bookslist),
			content_type='application/json')
		self.assertIn('book_created', str(res.data))
		res = self.client().get('/api/v2/books')
		self.assertEqual(res.status_code, 200)
		self.assertIn('hello books', str(res.data))

	def test_api_can_get_book_by_id(self):
		"""test api GET book by ID"""
		res = self.client().post(
			'/api/v2/books',
			data=json.dumps(self.bookslist),
			content_type='application/json')
		self.assertEqual(res.status_code, 201)
		result_in_json = json.loads(res.data.decode('utf-8').replace("'", "\""))
		result = self.client().get('/api/v2/books/{result_in_json["book_created"]["id"]}')
		self.assertIn('hello books', str(res.data))

	def test_api_no_json(self):
		"""test api detects no JSON """
		book = {'title': 'Armin vaan Buuren', 'isbn': '6255415789'}
		res = self.client().post('/api/v2/books', data=json.dumps(book), content_type='application/json')
		self.assertEqual(res.status_code, 201)
		self.assertIn('armin', str(res.data))
		book = {}
		res = self.client().put(
			'/api/v2/books/1',
			data=json.dumps(book),
			content_type='application/json')
		self.assertEqual(res.status_code, 400)

	def test_api_update_book_not_found(self):
		"""test api book with id not found"""
		res = self.client().put(
			'/api/v2/books/1',
			data=json.dumps({'title': "from the grave"}),
			content_type='application/json')
		self.assertEqual(res.status_code, 404)

	def test_api_book_can_be_edited(self):
		"""test api PUT book updates book"""
		book = {'title': 'Armin vaan Buuren', 'isbn': '6255415789'}
		res = self.client().post('/api/v2/books', data=json.dumps(book), content_type='application/json')
		self.assertEqual(res.status_code, 201)
		self.assertIn('armin', str(res.data))
		res = self.client().put(
			'/api/v2/books/1',
			data=json.dumps({'title': "from the grave"}),
			content_type='application/json')
		result = self.client().get('/api/v2/books/1')
		self.assertIn('from the grave', str(result.data))

	def test_api_update_book_validation_error(self):
		"""test api throws a validation error for the schema"""
		book = {'title': 'Armin vaan Buuren', 'isbn': '6255415789'}
		res = self.client().post('/api/v2/books', data=json.dumps(book), content_type='application/json')
		self.assertEqual(res.status_code, 201)
		self.assertIn('armin', str(res.data))
		res = self.client().put(
			'/api/v2/books/1',
			data=json.dumps({'title': "from the grave", "ola": "kilo"}),
			content_type='application/json')
		self.assertIn('unknown field', str(res.data))

	def test_api_book_delete(self):
		"""test api DELETE removes book"""
		book = {'title': 'Armin vaan Buuren', 'isbn': '6255415789'}
		res = self.client().post('/api/v2/books', data=json.dumps(book), content_type='application/json')
		self.assertEqual(res.status_code, 201)
		self.assertIn('armin', str(res.data))
		rv = self.client().delete('/api/v2/books/1')
		self.assertEqual(rv.status_code, 200)

		# Test book search returns 404
		result = self.client().get('/api/v2/books/1')
		self.assertEqual(result.status_code, 404)

	def test_delete_book_not_found(self):
		"""test api returns no book found"""
		rv = self.client().delete('/api/v2/books/1')
		self.assertEqual(rv.status_code, 404)


if __name__ == "__main__":
	unittest.main()
