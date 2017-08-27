import os, sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)+'../..'))

# DEBUG = True
# postgres = {
	# 'user':'test_user',
	# 'password':'password',
	# 'host':'localhost',
	# 'port':'5432',
	# 'database':'test_db'
# }
# 

# postgres = {
	# 'user':'uhxtsfsntzmrte',
	# 'password':'5b9bd82112044c5a4ffa426cb9e49e25dba3a983306dfd1d0d90262eaf47c7fe',
	# 'host':'ec2-107-22-160-199.compute-1.amazonaws.com',
	# 'port':'5432',
	# 'database':'ddmse7dnb9n41q'
# }
# 
# SQLALCHEMY_DATABASE_URI = 'postgres://{user}:{password}@{host}:{port}/{database}'.format(user=postgres['user'], password=postgres['password'], host=postgres['host'], port=postgres['port'], database=postgres['database'])


# note: tehse values were obtained from the heroku dashboard: settins>reveal config vars

# all this doesn't work yet ^ temporary fix below

basedir = os.path.abspath(os.path.dirname(__file__))
DATABASE = 'fidelity.db'
DATABASE_PATH = os.path.join(basedir, DATABASE)
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_PATH

