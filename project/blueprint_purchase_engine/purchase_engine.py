import flask
from flask import Blueprint, render_template, url_for, redirect, request, send_from_directory, send_file, session
from project import db, app
from project.models import purchase_key
from werkzeug.datastructures import ImmutableOrderedMultiDict
import requests, string, random, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
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



@purchase_engine.route('/download/<book>/<customer_key>', methods=['GET'])
def download(book, customer_key):
	key = db.session.query(purchase_key).filter_by(key=customer_key).first()
	if key:
		db.session.delete(key)
		db.session.commit()
		return send_file('book_pdfs/{}.pdf'.format(book), as_attachment=True, attachment_filename='namethiswhatyouwant.pdf')
	else:
		return 'The purchase key is either invalid or already used.'





# attempted heroku workaround: doesn't download from browser, simply displays encrypted/corrupt version (I'm not sure which)







# @purchase_engine.route('/download/<book>/<customer_key>', methods=['GET', 'POST'])
# def download(book, customer_key):
	# url = 'http://127.0.0.1:5000/api/v1'
	# data = {'book' : book, 'key' : customer_key} #add authentication key and verification here
	# headers = {'Content-Type' : 'application/json'}
	# r = requests.post(url, data=json.dumps(data), headers=headers) # 1. sends customer download request to api
	# # delete_key sends json back here #auth code verified here
	# if request.method == 'POST':
		# json_data = request.get_json()
		# if json_data['auth'] == 's0?3di+y[+L!Yxdk=XdDMR/!;hT?&': # 6. checks for internal authentication key
			# book = json_data['book']
			# return send_file('book_pdfs/{}.pdf'.format(data['book']), as_attachment=True, attachment_filename='namethiswhatyouwant.pdf') # 7. downloads book
	# return r.text
# 
# 
# @purchase_engine.route('/api/v1', methods=['GET', 'POST'])
# def api_handler():
	# if request.method == 'POST':
		# book_key_json = request.get_json() #force is necessary if for some reason (human error or otherwise) the MIME type isn't set
		# key = book_key_json["key"]
		# book = book_key_json["book"]		
		# key_query = db.session.query(purchase_key).filter_by(key=key).first() # 2. api takes information from download request and checks key against db
# 	
		# if key_query:
			# url = 'http://127.0.0.1:5000/delete_key'
			# data = {'book' : book, 'key' : key, 'request_source_auth' : 's0?3di+y[+L!Yxdk=XdDMR/!;hT?&'} # 3. if customerkey passes, an internal authentication key is added to the data (so in final download the only post requests that can trigger a download MUST have coem from here, not a hacker)
			# headers = {'Content-Type' : 'application/json'}
			# r = requests.post(url, data=json.dumps(data), headers=headers)
			# return r.text
# 
		# else: # if an invalid or used key is used THIS is where it 'should' abort the operation.
			# return 'key is invalid or expired.'
# 
# @purchase_engine.route('/delete_key', methods=['POST'])
# def delete_key():
	# if request.method == 'POST':
		# book_key_json = request.get_json()
		# key = book_key_json["key"]
		# book = book_key_json["book"]
		# auth_code = book_key_json["request_source_auth"]
		# key_query = db.session.query(purchase_key).filter_by(key=key).first() # D.R.Y?
		# db.session.delete(key_query)                                                    # 4. the key is deleted from the database
		# db.session.commit()
		# url = 'http://127.0.0.1:5000/download/{}/{}'.format(book, key)
		# data = {'book' : book, 'auth':auth_code} ###!!!!!!! CODE SMELL !!!!!! ####
		# headers = {'Content-Type' : 'application/json'}
		# r = requests.post(url, data=json.dumps(data), headers=headers)  # 5. json is posted back to the inital page the customer clicked trigerring the download, note the auth code
		# return r.text


@purchase_engine.route('/free_book', methods=['GET', 'POST'])
def free_book():
	if request.method == 'POST':
		if request.form['username'] == 'admin' and request.form['password'] == 'admin':
			email = request.form['email']
			book = request.form['book']
			send_book_link(email, book)
	return render_template('free_book.html')


# refract this code to make a 'download book' helper function which takes the parameters: book, email and does everything else to send the download email