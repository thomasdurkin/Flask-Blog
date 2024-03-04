from flask import render_template, url_for, flash, redirect, request, abort, Blueprint
from flask_login import current_user, login_required, login_user, logout_user
from flaskblog import db, bcrypt
from flaskblog.models import User, Post
from flaskblog.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from flaskblog.users.utils import save_picture, send_reset_email

users = Blueprint('users', __name__)


@users.route("/register", methods = ['GET', 'POST'])
def register():
	# Check if user is already logged in
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

		# Create a new user
		user = User(username = form.username.data,
			  		email = form.email.data,
					password = hashed_password)
		db.session.add(user)
		db.session.commit()

		flash('Your account has been created!', 'success')
		return redirect(url_for('users.login'))
	
	return render_template('register.html', title = 'Register', form = form)


@users.route("/login", methods = ['GET', 'POST'])
def login():
	# Check if user is already logged in
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	
	form = LoginForm()
	if form.validate_on_submit():
		# Get user by email
		user = User.query.filter_by(email = form.email.data).first()
		# Check user exists and password matches
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember = form.remember.data)
			# Redirect user to correct page if they tried to access it without login
			next_page = request.args.get('next')
			return redirect(next_page) if next_page else redirect(url_for('main.home'))
		else:
			flash('Login Failed. Please check email and password', 'danger')
			
	return render_template('login.html', title = 'Login', form = form)


@users.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('users.login'))


@users.route("/account", methods = ['GET', 'POST'])
@login_required
def account():
	form = UpdateAccountForm()
	if form.validate_on_submit():
		# Update Picture
		if form.picture.data:
			picture_file = save_picture(form.picture.data)
			current_user.img_file = picture_file
		# Update Username and Email
		current_user.username = form.username.data
		current_user.email = form.email.data
		db.session.commit()
		flash('Your account has been updated!', 'success')
		return redirect(url_for('users.account'))
	# Auto fill form with current info
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email

	img_file = url_for('static', filename = 'profile_pics/' + current_user.img_file)
	return render_template('account.html', 
							title = 'Account', 
							image_file = img_file, 
							form = form)


@users.route("/user/<string:username>")
def user_posts(username):
	page = request.args.get('page', 1, type = int)
	# Get specific user
	user = User.query.filter_by(username = username).first_or_404()
	# Get posts for the selected user
	posts = Post.query\
				.filter_by(author = user)\
				.order_by(Post.date_posted.desc())\
				.paginate(page = page, per_page=4)
	
	return render_template('user_posts.html', posts = posts, user = user)


@users.route("/reset_password", methods = ['GET', 'POST'])
def reset_request():
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	
	form = RequestResetForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email = form.email.data).first()
		send_reset_email(user)
		flash('An email has been sent with instructions to reset your password.', 'info')
		return redirect(url_for('users.login'))
	
	return render_template('reset_request.html', title = 'Reset Password', form = form)


@users.route("/reset_password/<token>", methods = ['GET', 'POST'])
def reset_token(token):
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	
	user = User.verify_reset_token(token)
	if not user:
		flash('That is an invalid or expired token.', 'warning')
		return redirect(url_for('users.reset_request'))
	
	form = ResetPasswordForm()
	# Update user password
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user.password = hashed_password
		db.session.commit()
		flash('Your password has been updated!', 'success')
		return redirect(url_for('users.login'))
	
	return render_template('reset_token.html', title = 'Reset Password', form = form)