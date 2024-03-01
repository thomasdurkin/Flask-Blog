from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)
app.app_context().push()
app.config['SECRET_KEY'] = '6f5371ffabcc0f1c9ff9cb95554336f0'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
# Setup environment variables
app.config['MAIL_USERNAME'] = ''
app.config['MAIL_PASSWORD'] = ''

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
mail = Mail(app)

login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from flaskblog import routes