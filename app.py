from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from flask import Flask, render_template, request, redirect, url_for
from random import shuffle

# test database
DATABASE_URL = "postgresql://pun:pun@localhost:5432/booksdb"

engine = create_engine(DATABASE_URL)
db = scoped_session(sessionmaker(bind=engine))

app = Flask(__name__)

user = None

@app.route("/")
def index():

    books = db.execute("SELECT * FROM books").fetchall()
    shuffle(books)
    books = books[0:25]

    return render_template('index.html', books=books)

@app.route("/book/isbn/<isbn>")
def book(isbn):

    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn":isbn}).fetchone()

    return render_template('book.html', book=book)

@app.route("/book/author/<author>")
def book_author(author):

    books = db.execute("SELECT * FROM books WHERE author = :author", {"author":author}).fetchall()

    return render_template('book_author.html', author=author, books=books)

@app.route("/search", methods=["POST"])
def search():

    opt = request.form.get("opt")
    key = request.form.get("key")

    if opt == "author":
        books =  db.execute("SELECT * FROM books WHERE LOWER(author) LIKE LOWER(:key)", {"key":'%'+key+'%'}).fetchall()
    elif opt == "title":
        books =db.execute("SELECT * FROM books WHERE LOWER(title) LIKE LOWER(:key)", {"key":'%'+key+'%'}).fetchall()
    elif opt == "isbn":
        books =  db.execute("SELECT * FROM books WHERE LOWER(isbn) LIKE LOWER(:key)", {"key":'%'+key+'%'}).fetchall()
    else:
        return '404 not found'

    if books == []:
        return '404 not found'

    return render_template('search.html', books=books, key=key, opt=opt)
    