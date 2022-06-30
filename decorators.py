from functools import wraps
from flask import request, redirect, url_for, session
import os

def isOwner(database):
	def decorator(f):
		@wraps(f)
		def decorated_function(*args,**kwargs):
			if os.environ["FLASK_ENV"]!="development":
				return redirect('page_not_found')
			if not 'user_uuid' in  session.keys() or  database.owner.find_one({'user_uuid':session.get('user_uuid', "xxxxxxxx")}) is None:
				return redirect(url_for('login'))
			return f(*args, **kwargs)
		return decorated_function
	return decorator 