from functools import wraps
from flask import request, redirect, url_for, session

def isOwner(database):
	def decorator(f):
		@wraps(f)
		def decorated_function(*args,**kwargs):
			if database.owner.find_one({'user_uuid':str(session['user_uuid'])}) is None:
				return redirect(url_for('login'))
			return f(*args, **kwargs)
		return decorated_function
	return decorator