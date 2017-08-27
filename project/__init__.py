import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '../..'))

from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask.ext.heroku import Heroku

app = Flask(__name__)
app.config.from_pyfile('_config.py')
heroku = Heroku(app)
db = SQLAlchemy(app)

# from project._config import postgres
# import psycopg2
# conn = psycopg2.connect(
	# database=postgres['database'],
	# user=postgres['user'],
	# password=postgres['password'],
	# host=postgres['host'],
	# port=postgres['port'])

from project.blueprint_base.base import base
from project.blueprint_books.books import books
from project.blueprint_purchase_engine.purchase_engine import purchase_engine

app.register_blueprint(base)
app.register_blueprint(books)
app.register_blueprint(purchase_engine)


##########
###TODO###
##########

# remove footer from contact page