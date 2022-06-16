from functools import wraps
from flask import request, redirect, url_for

def isOwner(database):
	def decorator(f):
		@wraps(f)
		def decorated_function(*args,**kwargs):
			if database.owner.find_one({'user_addr':str(request.remote_addr)}) is None:
				return redirect(url_for('login'))
			return f(*args, **kwargs)
		return decorated_function
	return decorator