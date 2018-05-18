import unittest
import json
from app import create_app, db


class AuthTestCase(unittest.TestCase):
	"""test api authentication"""

	def setUp(self):
		self.app = create_app(config_name="testing")
		# initialize the test client
		self.client = self.app.test_client
		# This is the user test json data with a predefined email and password
		self.user_data = {
			'username': 'tester',
			'email': 'tester@mail.com',
			'password': ',5Test_password',
			'is_admin': True
		}

		with self.app.app_context():
			# create all tables
			db.session.close()
			db.drop_all()
			db.create_all()

	def test_registration(self):
		"""test api can register user"""
		res = self.client().post(
			'/api/v2/auth/register',
			data=json.dumps(self.user_data),
			content_type='application/json'
		)
		# get the results returned in json format
		result = json.loads(res.data.decode())
		# assert that the request contains a success message and a 201 status code
		self.assertEqual(result['message'], "you successfully registered")
		self.assertEqual(res.status_code, 201)

	def test_already_registered_user(self):
		"""test api user already exists"""
		res = self.client().post(
			'/api/v2/auth/register',
			data=json.dumps(self.user_data),
			content_type='application/json')
		self.assertEqual(res.status_code, 201)
		second_res = self.client().post(
			'/api/v2/auth/register',
			data=json.dumps(self.user_data),
			content_type='application/json')
		self.assertEqual(second_res.status_code, 202)
		# get the results returned in json format
		result = json.loads(second_res.data.decode())
		self.assertEqual(
			result['message'], "user already exists. Please login")

	def test_auth_no_json_error(self):
		"""test api throws error if JSON not detected"""
		user = {}
		res = self.client().post(
			'/api/v2/auth/register',
			data=json.dumps(user),
			content_type='application/json')
		self.assertEqual(res.status_code, 400)

	def test_auth_key_missing_error(self):
		"""test api returns validation error if key misses"""
		user = {
			'username': "pilo",
			'email': "4562"
		}
		res = self.client().post(
			'/api/v2/auth/register',
			data=json.dumps(user),
			content_type='application/json')
		self.assertEqual(res.status_code, 401)
		self.assertIn('error', str(res.data))

	def test_auth_user_login(self):
		"""test api can log in user"""
		res = self.client().post(
			'/api/v2/auth/register',
			data=json.dumps(self.user_data),
			content_type='application/json')
		self.assertEqual(res.status_code, 201)

		user_data = {
			'username': 'tester',
			'email': 'tester@mail.com',
			'password': ',5Test_password'
		}
		login_res = self.client().post(
			'/api/v2/auth/login',
			data=json.dumps(user_data),
			content_type='application/json')

		result = json.loads(login_res.get_data(as_text=True))
		self.assertEqual(result['message'], 'successfully logged in')
		self.assertEqual(result.status_code, 200)
		self.assertTrue(result['access_token'])

	def test_auth_user_not_registered_cant_log_in(self):
		"""test api can't login in non registered user"""

		fake_user = {
			'username': "faker",
			'password': "faker_faker#R",
			'email': 'fake@mail.com'
		}

		res = self.client().post(
			'/api/v2/auth/login',
			data=json.dumps(fake_user),
			content_type='application/json')

		self.assertEqual(res.status_code, 404)
