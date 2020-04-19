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
#user = db.execute("SELECT * FROM users WHERE username = 'master'").fetchone()

# section 1 main book data
@app.route("/")
def index():

    books = db.execute("SELECT * FROM books").fetchall()
    shuffle(books)
    books = books[0:25]

    return render_template('index.html', books=books, user=user)

@app.route("/book/isbn/<isbn>")
def book(isbn):

    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn":isbn}).fetchone()

    return render_template('book.html', book=book, user=user)

@app.route("/book/author/<author>")
def book_author(author):

    books = db.execute("SELECT * FROM books WHERE author = :author", {"author":author}).fetchall()

    return render_template('book_author.html', author=author, books=books, user=user)

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

    return render_template('search.html', books=books, key=key, opt=opt, user=user)

# section 2 account, login, logout, register
@app.route("/account/<username>")
def account(username):

    return render_template('account.html', username=username)

@app.route("/account/login", methods=["POST"])
def login():

    username = request.form.get("username")
    password = request.form.get("password")

    global user
    user = db.execute("SELECT * FROM users WHERE \
                    username = :username AND \
                    password = :password", \
                    {"username":username, "password":password}).fetchone()

    if user == None:
        return 'Invalid username/password'

    return redirect(url_for('index'))

@app.route("/account/register")
def register():

    return render_template('account_register.html')

@app.route("/account/register/progess", methods=["POST"])
def register_progess():

    username = request.form.get("username")
    password = request.form.get("password")
    con_pass = request.form.get("con_pass")

    check = db.execute("SELECT username FROM users WHERE username = :username", {"username":username}).fetchone()

    if check != None or con_pass != password:
        return 'username already exist / password not match'

    db.execute("INSERT INTO users (username, password) \
                VALUES (:username, :password)", \
                {"username":username, "password":password})
    db.commit()

    return 'registration complete'

@app.route("/account/logout")
def logout():

    global user
    user = None

    return redirect(url_for('index'))