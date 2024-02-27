from flask import render_template, url_for, flash, redirect, request
from flaskblog import app, db, bcrypt
from flaskblog.models import User, Post
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm
from flask_login import login_user, current_user, logout_user, login_required
from PIL import Image

import secrets
import os

posts = [
	{
		'author' : 'Thomas Durkin',
		'title' : "Blog Post 1",
		'content' : 'First post content',
		'date_posted' : 'April 20, 2018'
	},
	{
		'author' : 'Thomas Durkin',
		'title' : "Blog Post 2",
		'content' : 'Second post content',
		'date_posted' : 'April 25, 2018'
	}
]
 
@app.route("/")
@app.route("/home")
def home():
	return render_template('home.html', posts = posts)

@app.route("/about")
def about():
	return render_template('about.html', title = 'About')

@app.route("/register", methods = ['GET', 'POST'])
def register():
	# Check if user is already logged in
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	
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
		return redirect(url_for('login'))
	
	return render_template('register.html', title = 'Register', form = form)

@app.route("/login", methods = ['GET', 'POST'])
def login():
	# Check if user is already logged in
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	
	form = LoginForm()
	if form.validate_on_submit():
		# Get user by email
		user = User.query.filter_by(email = form.email.data).first()
		# Check user exists and password matches
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember = form.remember.data)
			# Redirect user to correct page if they tried to access it without login
			next_page = request.args.get('next')
			return redirect(next_page) if next_page else redirect(url_for('home'))
		else:
			flash('Login Failed. Please check email and password', 'danger')
			
	return render_template('login.html', title = 'Login', form = form)

@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('login'))


def save_picture(picture):
	random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(picture.filename)
	picture_fn = random_hex + f_ext
	picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

	output_size = (125,125)
	img = Image.open(picture)
	img.thumbnail(output_size)
	img.save(picture_path)
	
	return picture_fn

@app.route("/account", methods = ['GET', 'POST'])
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
		return redirect(url_for('account'))
	# Auto fill form with current info
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email

	img_file = url_for('static', filename = 'profile_pics/' + current_user.img_file)
	return render_template('account.html', 
							title = 'Account', 
							image_file = img_file, 
							form = form)