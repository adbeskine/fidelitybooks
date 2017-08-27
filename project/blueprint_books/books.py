from flask import Blueprint, render_template, url_for, request

books = Blueprint('books', 'project', static_folder='static')

@books.route('/smoke_and_drug_free_children')
def book_smoking_book():
	return render_template('book_smoking_book.html')

@books.route('/builders')
def book_cowboy_builders():
	return render_template('book_cowboy_builders.html')

@books.route('/just_jokes_ok')
def book_just_jokes_ok():
	return render_template('book_just_jokes_ok.html')

@books.route('/twenty_one_rules')
def book_twenty_one_rules():
	return render_template('book_twenty_one_rules.html')

@books.route('/granite_worktops')
def book_granite_worktops():
	return render_template('book_granite_worktops.html')