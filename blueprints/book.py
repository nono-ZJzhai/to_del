from flask import Blueprint, render_template, request, redirect, url_for, session, g
from models.book import Book
from exts import db

bp = Blueprint('book', __name__)

@bp.route('/publish', methods=['GET', 'POST'])
def publish():
    if request.method == 'POST':
        title = request.form.get('title')
        isbn = request.form.get('isbn')
        category = request.form.get('category')
        condition = request.form.get('condition')
        price = request.form.get('price')
        location = request.form.get('location')
        contact = request.form.get('contact')
        
        book = Book(
            title=title,
            isbn=isbn,
            category=category,
            condition=condition,
            price=float(price),
            location=location,
            contact=contact,
            seller_id=session.get('user_id')
        )
        db.session.add(book)
        db.session.commit()
        return redirect(url_for('front.index'))
    return render_template('book/publish.html')

@bp.route('/detail/<int:book_id>')
def detail(book_id):
    book = Book.query.get(book_id)
    return render_template('book/detail.html', book=book)

@bp.route('/buy/<int:book_id>')
def buy(book_id):
    book = Book.query.get(book_id)
    if book and book.status == '未售出':
        book.status = '等待确认收货'
        db.session.commit()
    return redirect(url_for('book.detail', book_id=book_id))

@bp.route('/confirm/<int:book_id>')
def confirm(book_id):
    book = Book.query.get(book_id)
    if book and book.status == '等待确认收货':
        book.status = '已售出'
        db.session.commit()
    return redirect(url_for('book.detail', book_id=book_id))