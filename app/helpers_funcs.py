from functools import wraps
from flask import request, jsonify, current_app, make_response, abort
import jwt
from app.models import APIUser


def token_required(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		token = None

		if 'Authorization' in request.headers:
			auth_header = request.headers.get('Authorization')
			try:
				token = auth_header.split(" ")[1]
			except IndexError:
				return make_response(jsonify({
					'error': 'provide a valid auth token'
				})), 403

		if not token:
			return make_response(jsonify({'error': 'token is missing'})), 401

		try:
			decode_response = APIUser.decode_token(token)
			current_user = APIUser.query.filter_by(id=decode_response).first()
		except:
			message = 'Invalid token'
			if isinstance(decode_response, str):
				message = decode_response
			return make_response(jsonify({
				'status': 'failed',
				'message': message
			})), 401

		return f(current_user, *args, **kwargs)

	return decorated


def check_admin(user):
	"""
	Prevent non-admins from accessing the page
	:return: 403
	"""
	if not user.is_admin:
		abort(403)
