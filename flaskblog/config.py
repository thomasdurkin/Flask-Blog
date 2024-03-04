

class Config():
	SECRET_KEY = '6f5371ffabcc0f1c9ff9cb95554336f0'
	SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
	MAIL_SERVER = 'smtp.googlemail.com'
	MAIL_PORT = 587
	MAIL_USE_TLS = True
	# Setup environment variables
	MAIL_USERNAME = ''
	MAIL_PASSWORD = ''