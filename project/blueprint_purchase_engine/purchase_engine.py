import flask
from flask import Blueprint, render_template, url_for, redirect, request, send_from_directory, send_file
from project import db, app
from project.models import purchase_key
from werkzeug.datastructures import ImmutableOrderedMultiDict
import requests, string, random, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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

def download_page():
	return render_template('download.html', book=book)

#-------------------------------------#

purchase_engine = Blueprint('purchase_engine', 'project')

@purchase_engine.route('/ipn/', methods=['POST'])
def ipn():
	arg = ''
	request.parameter_storage_class = ImmutableOrderedMultiDict
	values = request.form
	for x,y in values.items():
		arg += "&{x}={y}".format(x=x, y=y)
	validate_url = 'https://www.paypal.com/cgi-bin/webscr?cmd=_notify-validate{arg}'.format(arg=arg)
	r = requests.get(validate_url)
	if r.text == 'VERIFIED':
		try:
			if request.form['option_selection1']:
				email = request.form['option_selection1']
			else:
				email = request.form['payer_email']
			key = key_generator()
			book = request.form['custom']
			download_url = 'https://fidelitybooks.herokuapp.com/download/{book}/{key}'.format(book=book, key=key)
			
			# save the key to the database
			try:
				db_key = purchase_key(key)
				db.session.add(db_key)
				db.session.commit()
			except Exception as e:
				send_email(
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
			return r.text
			#source: http://naelshiab.com/tutorial-send-email-python/
		except Exception as e: #really this should be sent from fidelity to the developers LIVE email
			send_email(
				fromaddr = 'fidelitydevv@gmail.com',
				fromaddr_password = 'afgu6799',
				toaddr = 'a.d.beskine@outlook.com',
				subject = 'FIDELITYBOOKS PURCHASE ENGINE ERROR',
				text = 'if you are receiving this a live customer has experienced a purchase error:\n\n DATA:\n{data}\n\n\n{e}'.format(data = str(values), e=e)
				)
	return 'this is working'




@purchase_engine.route('/success/')
def success():
	return render_template('purchase_success.html')
	# render basic template saying something along the lines of "purchase successful a download link has been sent to your email"

@purchase_engine.route('/download/<book>/<customer_key>', methods=['GET'])
def download(book, customer_key):
	key_check = db.session.query(purchase_key).filter_by(key=customer_key).first()
	if key_check:
		# db.session.delete(key_check)
		# db.session.commit()
		return send_file('book_pdfs/{}.pdf'.format(book), as_attachment=True, attachment_filename='namethiswhatyouwant.pdf')
	
	else:
		return 'The purchase key is either invalid or already used.'

@purchase_engine.route('/free_book', methods=['GET', 'POST'])
def free_book():
	if request.method == 'POST':
		if request.form['username'] == 'admin' and request.form['password'] == 'admin':
			email = request.form['email']
			book = request.form['book']
			key = key_generator()
			download_url = 'https://fidelitybooks.herokuapp.com/download/{book}/{key}'.format(book=book, key=key)
			db_key = purchase_key(key)
			db.session.add(db_key)
			db.session.commit()
			send_email(
				fromaddr = 'fidelitydevv@gmail.com',
				fromaddr_password = 'afgu6799',
				toaddr = email,
				subject = 'Thank you for your purchase from Fidelity Books!',
				text = "Hello,\nThank you for your purchase, you can download your book here:\n{download_url}\nplease note this download link expires after one download.".format(download_url=download_url)
				)
	return render_template('free_book.html')


################################
####DRY AND CODE SMELL ALERT####
################################

# refract free_book and ipn so as to not repeat download url = etc etc


# refract this code to make a 'download book' helper function which takes the parameters: book, email and does everything else to send the download email