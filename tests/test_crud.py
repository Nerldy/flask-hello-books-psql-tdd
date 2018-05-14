import unittest
import os
from flask import json
from app import create_app, db


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
		res = self.client().post('/api/v2/books', data=self.bookslist)
		self.assertEqual(res.status_code, 201)
		self.assertIn('book_created', str(res.data))

	def test_api_gets_all_books(self):
		"""test api GET all books"""
		res = self.client().post('/api/v2/books', data=self.bookslist)
		self.assertIn('book_created', str(res.data))
		res = self.client().get('/api/v2/books')
		self.assertEqual(res.status_code, 200)
		self.assertIn('hello books', str(res.data))

	def test_api_can_get_book_by_id(self):
		"""test api GET book by ID"""
		res = self.client().post('/api/v2/books', data=self.bookslist)
		self.assertEqual(res.status_code, 201)
		result_in_json = json.loads(res.data.decode('utf-8').replace("'", "\""))
		result = self.client().get(f'/api/v2/books/{result_in_json["id"]}')
		self.assertEqual(result.status_code, 200)
		self.assertIn('hello books', str(res.data))

	def test_api_book_can_be_edited(self):
		"""test api PUT book updates book"""
		book = {'title': 'Armin vaan Buuren', 'isbn': '6255415789'}
		res = self.client().post('/api/v2/books', data=book)
		self.assertEqual(res.status_code, 201)
		self.assertIn('armin', str(res.data))
		res = self.client().put('/api/v2/books/1', data={'title': "from the grave"})
		result = self.client().get('/api/v2/books/1')
		self.assertIn('from the grave', str(result.data))

	def test_api_book_delete(self):
		"""test api DELETE removes book"""
		book = {'title': 'Armin vaan Buuren', 'isbn': '6255415789'}
		res = self.client().post('/api/v2/books', data=book)
		self.assertEqual(res.status_code, 201)
		self.assertIn('armin', str(res.data))
		rv = self.client().delete('/api/v2/books/1')
		self.assertEqual(rv.status_code, 200)

		# Test book search returns 404
		result = self.client().get('/api/v2/books/1')
		self.assertEqual(result.status_code, 404)


if __name__ == "__main__":
	unittest.main()
