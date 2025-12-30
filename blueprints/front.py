from flask import Blueprint, render_template, g
from models.book import Book

bp = Blueprint('front', __name__)

@bp.route('/')
def index():
    books = Book.query.all()
    return render_template('front/index.html', books=books)

@bp.route('/category/<category>')
def category_books(category):
    books = Book.query.filter_by(category=category).all()
    return render_template('front/index.html', books=books)