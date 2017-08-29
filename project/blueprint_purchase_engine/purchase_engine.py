import flask
from flask import Blueprint, render_template, url_for, redirect, request, send_from_directory, send_file, session
from project import db, app
from project.models import purchase_key
from werkzeug.datastructures import ImmutableOrderedMultiDict
import requests, string, random, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json, sys, os
from PyPDF2 import PdfFileReader, PdfFileWriter

sys.path.append(os.path.abspath(os.path.dirname(__file__)+'../..'))
######################
####HELPER METHODS####
######################
def key_generator():
	return ''.join(random.SystemRandom().choices(string.ascii_letters + string.digits, k=15))

def send_email(fromaddr, fromaddr_password, toaddr, subject, text): #note, set up for gmail only currently
	msg = MIMEMultipart()
	msg['FROM'] = fromaddr
	msg['TO'] = toaddr
	msg['Subject'] = subject
	body = text

	msg.attach(MIMEText(body, 'plain'))
	server=smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()
	server.login(fromaddr, fromaddr_password)
	text = msg.as_string()
	server.sendmail(fromaddr, toaddr, text)
	server.quit()
	#source: http://naelshiab.com/tutorial-send-email-python/

def send_book_link(email, book):
	key=key_generator()
	download_url = 'https://fidelitybooks.co.uk/download/{book}/{key}'.format(book=book, key=key)
	try:
		db_key = purchase_key(key)
		db.session.add(db_key)
		db.session.commit()
	except Exception as e:
		return send_email(
		fromaddr = 'fidelitydevv@gmail.com',
		fromaddr_password = 'afgu6799',
		toaddr = 'a.d.beskine@outlook.com',
		subject = 'FIDELITYBOOKS PURCHASE ENGINE ERROR',
		text = 'if you are receiving this a live customer has experienced a purchase error:\n\n DATA:{e}'.format(e=e)
		)		
		# send the email
	send_email(
		fromaddr = 'fidelitydevv@gmail.com',
		fromaddr_password = 'afgu6799',
		toaddr = email,
		subject = 'Thank you for your purchase from Fidelity Books!',
		text = "Hello,\nThank you for your purchase, you can download your book here:\n{download_url}\nplease note this download link expires after one download.".format(download_url=download_url)
		)



#-------------------------------------#

purchase_engine = Blueprint('purchase_engine', 'project')

@purchase_engine.route('/ipn/', methods=['POST'])
def ipn():
	arg = '' # this takes the ipn paypal sends and interprets it
	request.parameter_storage_class = ImmutableOrderedMultiDict
	values = request.form
	try:
		for x,y in values.items():
			arg += "&{x}={y}".format(x=x, y=y)
		validate_url = 'https://www.paypal.com/cgi-bin/webscr?cmd=_notify-validate{arg}'.format(arg=arg)
		r = requests.get(validate_url)
		if r.text == 'VERIFIED':
			if request.form['option_selection1']:
				email = request.form['option_selection1']
			else:
				email = request.form['payer_email']
			book = request.form['custom']
			send_book_link(email, book)
	except Exception as e:
		return send_email(
		fromaddr = 'fidelitydevv@gmail.com',
		fromaddr_password = 'afgu6799',
		toaddr = 'a.d.beskine@outlook.com',
		subject = 'FIDELITYBOOKS PURCHASE ENGINE ERROR',
		text = 'if you are receiving this a live customer has experienced a purchase error:\n\n{values}\n\nDATA:{e}'.format(values=values, e=e)
		)	
	return 'this is working'



@purchase_engine.route('/success/')
def success():
	return render_template('purchase_success.html')


# works perfecly offline, online it deletes the key then says purchase key is invalid (I have commented out code to deduce this is the case.)

@purchase_engine.route('/download/<book>/<customer_key>', methods=['GET'])
def download(book, customer_key):
	key = db.session.query(purchase_key).filter_by(key=customer_key).first()
	if key:
		db.session.delete(key)
		db.session.commit()
		return send_file('book_pdfs/{}.pdf'.format(book), as_attachment=True, attachment_filename='namethiswhatyouwant.pdf')
	else:
		return 'The purchase key is either invalid or already used.'

@purchase_engine.route('/free_book', methods=['GET', 'POST'])
def free_book():
	if request.method == 'POST':
		if request.form['username'] == 'admin' and request.form['password'] == 'admin':
			email = request.form['email']
			book = request.form['book']
			send_book_link(email, book)
	return render_template('free_book.html')


# refract this code to make a 'download book' helper function which takes the parameters: book, email and does everything else to send the download email