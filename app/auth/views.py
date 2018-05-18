from . import auth_blueprint
from flask.views import MethodView
from flask import make_response, request, jsonify, abort
from app.models import Booklist, APIUser
from cerberus import Validator
from app import db
import re
import jwt

login_schema = {
	'username': {
		'type': 'string',
		'required': True
	},
	'email': {
		'type': 'string',
		'required': True
	},
	'password': {
		'type': 'string',
		'required': True,
	}
}

user_schema = {
	'username': {
		'type': 'string',
		'required': True,
		'minlength': 2,
		'maxlength': 50
	},
	'email': {
		'type': 'string',
		'required': True,
		'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',
		'maxlength': 100
	},
	'password': {
		'type': 'string',
		'required': True,
		'minlength': 2,
		'regex': '(?=^.{8,}$)((?=.*\d)|(?=.*\W+))(?![.\n])(?=.*[A-Z])(?=.*[a-z]).*$'

	},
	'is_admin': {
		'type': 'boolean',
		'required': False
	}
}

validate_user_schema = Validator(user_schema)
validate_login_schema = Validator(login_schema)


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


class RegistrationView(MethodView):
	"""registers a new use"""

	def post(self):
		"""handle POST request for /api/v2/auth/register"""

		post_data = request.get_json()

		if not post_data:
			abort(400)

		# check if uer already exists
		user = APIUser.query.filter(db.or_(
			APIUser.username == post_data['username'],
			APIUser.email == post_data['email']
		)).first()

		if not user:
			"""register user"""
			try:
				if validate_user_schema.validate(post_data):
					username = format_inputs(post_data['username'])
					email = post_data['email']
					password = post_data['password']

					new_user = APIUser(
						username=username,
						password=password,
						email=email
					)

					if 'is_admin' in post_data:
						new_user.is_admin = post_data['is_admin']
					new_user.save()

					return make_response(
						jsonify({
							'message': "you successfully registered"
						})
					), 201

				return jsonify({"error": validate_user_schema.errors}), 401

			except Exception as e:
				response = {
					'message': str(e)
				}

				return make_response(jsonify(response)), 401

		return make_response(
			jsonify({
				'message': "user already exists. Please login"
			})
		), 202


class Loginview(MethodView):
	"""this class handles user login"""

	def post(self):
		"""handle POST request for login view"""
		post_data = request.get_json()

		if not post_data:
			abort(400)

		user = APIUser.query.filter(
			db.and_(
				APIUser.username == post_data['username'],
				APIUser.email == post_data['email'],
			)).first()

		if not user:
			return jsonify({'error': "user not found. Please register"}), 401

		try:

			if validate_login_schema.validate(post_data):
				password = post_data['password']

				if user.verify_password(password=password):
					# Generate the access token. This will be used as the authorization header
					access_token = user.generate_token(user.id)
					print(access_token)

					if access_token:
						return make_response(jsonify(
							{
								'message': "successfully logged in",
								'access_token': access_token.decode()
							}
						)), 200

				return make_response(
					jsonify(
						{
							'error': 'invalid username, password or email. Try again.'
						}
					)
				), 401

			return jsonify({'error': validate_login_schema.errors}), 401
		except Exception as e:
			return make_response(
				jsonify({
					'message': str(e)
				})
			), 500


registration_view = RegistrationView.as_view('register_view')
login_view = Loginview.as_view('login_view')

auth_blueprint.add_url_rule(
	'/api/v2/auth/register',
	view_func=registration_view,
	methods=['POST'],
)

auth_blueprint.add_url_rule(
	'/api/v2/auth/login',
	view_func=login_view,
	methods=['POST'],
)
