from functools import wraps
from flask import request, jsonify, current_app
import jwt
from app.models import APIUser


def token_required(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		token = None

		if 'Authorization' in request.headers:
			token = request.headers['Authorization']

		if not token:
			return jsonify({'error': 'token is missing'}), 401

		try:
			data = jwt.decode(token, str(current_app.config['SECRET']))
			current_user = APIUser.query.filter_by(user_id=data['id']).first()
		except:
			return jsonify({'error': "token is invalid"}), 401

		return f(current_user, *args, **kwargs)

	return decorated

