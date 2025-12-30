from exts import db
from datetime import datetime

class Book(db.Model):
    __tablename__ = 'book'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(20), nullable=False, unique=True)
    category = db.Column(db.String(50), nullable=False)
    condition = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='未售出')
    location = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(50), nullable=False)
    publish_time = db.Column(db.DateTime, default=datetime.now)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    seller = db.relationship('User', backref='books')