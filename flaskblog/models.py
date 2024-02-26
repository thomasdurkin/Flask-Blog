from datetime import datetime
from flaskblog import db

class User(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(20), unique = True, nullable = False)
	email = db.Column(db.String(120), unique = True, nullable = False)
	img_file = db.Column(db.String(20), nullable = False, default = 'default.jpg')
	password = db.Column(db.String(60), nullable = False)
	# lazy defines when sqlalchemy will load the data
	posts = db.relationship('Post', backref = 'author', lazy = True)

	def __repr__(self):
		return f"User('{self.username}', '{self.email}', '{self.img_file}')"
	
class Post(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
	title = db.Column(db.String(100), nullable = False)
	date_posted = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
	content = db.Column(db.Text, nullable = False)

	def __repr__(self):
		return f"Post('{self.title}', '{self.date_posted}')"