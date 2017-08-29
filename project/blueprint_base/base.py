from flask import Blueprint, render_template, url_for

base = Blueprint('base', 'project', static_folder='static')

@base.route('/', methods=['GET', 'POST'])
def index():
	return render_template('index.html')

@base.route('/bookshop')
def bookshop():
	return render_template('bookshop.html')

@base.route('/authors')
def authors():
	return render_template('authors.html')

@base.route('/contact')
def contact():
	return render_template('contact.html')
	# TODO sort out form response