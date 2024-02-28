from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog import app, db, bcrypt
from flaskblog.models import User, Post
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from flask_login import login_user, current_user, logout_user, login_required
from PIL import Image

import secrets
import os
 
@app.route("/")
@app.route("/home")
def home():
	page = request.args.get('page', 1, type = int)
	# Pagination with 4 posts per page ordered by date
	posts = Post.query.order_by(Post.date_posted.desc()).paginate(page = page, per_page=4)
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

@app.route("/post/new", methods = ['GET', 'POST'])
@login_required
def new_post():
	form = PostForm()
	if form.validate_on_submit():
		post = Post(title = form.title.data,
			  		content = form.content.data,
					author = current_user)
		db.session.add(post)
		db.session.commit()
		flash('Your post has been created!', 'success')
		return redirect(url_for('home'))
	
	return render_template('create_post.html', 
							title = 'New Post', 
							form = form,
							legend = 'New Post')

@app.route("/post/<int:post_id>")
def post(post_id):
	# Return 404 error if post does not exist
	post = Post.query.get_or_404(post_id)
	print(post)
	return render_template('post.html', 
							title = post.title, 
							post = post)

@app.route("/post/<int:post_id>/update", methods = ['GET', 'POST'])
@login_required
def update_post(post_id):
	post = Post.query.get_or_404(post_id)
	
	if post.author != current_user:
		# Throw forbidden page error
		abort(403)
	
	form = PostForm()
	if form.validate_on_submit():
		post.title = form.title.data
		post.content = form.content.data
		db.session.commit()
		flash('Your Post has been updated!', 'success')
		return redirect(url_for('post', post_id=post.id))
	
	# Load data into form if GET request
	elif request.method == 'GET':
		form.title.data = post.title
		form.content.data = post.content

	return render_template('create_post.html', 
							title = 'Update Post', 
							form = form,
							legend = 'Update Post')

@app.route("/post/<int:post_id>/delete", methods = ['POST'])
@login_required
def delete_post(post_id):
	post = Post.query.get_or_404(post_id)
	
	if post.author != current_user:
		# Throw forbidden page error
		abort(403)

	db.session.delete(post)
	db.session.commit()
	flash('Your Post has been deleted.', 'success')

	return redirect(url_for('home'))


	