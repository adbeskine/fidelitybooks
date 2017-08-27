import flask
from flask import Blueprint, render_template, url_for, redirect, request, send_from_directory, send_file, session
from project import db, app
from project.models import purchase_key
from werkzeug.datastructures import ImmutableOrderedMultiDict
import requests, string, random, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import threading
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
	download_url = 'https://fidelitybooks.herokuapp.com/download/{book}/{key}'.format(book=book, key=key)
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
		text = 'if you are receiving this a live customer has experienced a purchase error:\n\n DATA:\n{data}\n\n\n{e}'.format(data = str(values), e=e)
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
	return 'this is working'




@purchase_engine.route('/success/')
def success():
	return render_template('purchase_success.html')
	# render basic template saying something along the lines of "purchase successful a download link has been sent to your email"


@purchase_engine.route('/download/<book>/<customer_key>', methods=['GET']) #add post here?
def download(book, customer_key):
	book_key_data = {'book': book, 'key': customer_key}
	requests.post('http://127.0.0.1:5000/api/v1', json=book_key_data) # url_for doesn't seem to work here for some reason...


@purchase_engine.route('/api/v1', methods=['POST'])
def api_handler():
	if request.method == 'POST':
		book_key_json = request.get_json(force=True) #force is necessary if for some reason (human error or otherwise) the MIME type isn't set
		book = book_key_json["book"]
		key = book_key_json["key"]
		
		key_query = db.session.query(purchase_key).filter_by(key=key).first()
		if key_query:
			key_data = {'key': key}
			book_data = {'book': book}
			requests.post('http://127.0.0.1:5000/delete_key', json=key_data)
			requests.post('http://127.0.0.1:5000/asfju644-95hafld', json=book_data)


@purchase_engine.route('/delete_key', methods=['POST'])
def delete_key():
	if request.method == 'POST':
		key_data = request.get_json(force=true)
		key = key_data["key"]
		key_query = db.session.query(purchase_key).filter_by(key=key).first() # D.R.Y?
		db.session.delete(key_query)
		db.session.commit()

@purchase_engine.route('/asfju644-95hafld', methods=['POST']) #anyone can just send a post request to this adress so must keep it unguessable
def send_book():
	if request.method=='POST':
		book_data = request.get_json(force=True)
		book = book_data["book"]
		return send_file('book_pdfs/{}.pdf'.format(book), as_attachment=True, attachment_filename='namethiswhatyouwant.pdf')


@purchase_engine.route('/free_book', methods=['GET', 'POST'])
def free_book():
	if request.method == 'POST':
		if request.form['username'] == 'admin' and request.form['password'] == 'admin':
			email = request.form['email']
			book = request.form['book']
			send_book_link(email, book)
	return render_template('free_book.html')


# refract this code to make a 'download book' helper function which takes the parameters: book, email and does everything else to send the download email