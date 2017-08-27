from project import db

class purchase_key(db.Model):

	__tablename__ = "purchase_key"

	Id = db.Column(db.Integer, primary_key = True)
	key = db.Column(db.String)

	def __init__(self, key):
		self.key = key

	def __repr__(self):
		return '<key is private>'