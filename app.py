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

    reviews = db.execute("SELECT * FROM reviews, books, users WHERE \
                            books.isbn = :isbn AND books.isbn = reviews.isbn AND users.user_id = reviews.user_id", \
                            {"isbn":isbn}).fetchall()
    reviews = reviews[::-1]

    if user != None:
        check = db.execute("SELECT * FROM reviews WHERE \
                            user_id = :user_id AND isbn = :isbn", \
                            {"user_id":user.user_id, "isbn":isbn}).fetchone()
    else:
        check = None

    return render_template('book.html', book=book, user=user, check=check, reviews=reviews)

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

    reviews = db.execute("SELECT * FROM reviews, books WHERE reviews.user_id = :user_id AND reviews.isbn = books.isbn" , {"user_id":user.user_id}).fetchall()
    reviews = reviews[::-1]

    return render_template('account.html', user=user, reviews=reviews)

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

# section 3 review and updatedb
@app.route("/book/isbn/<isbn>/review", methods=["POST"])
def review(isbn):

    review = request.form.get("review")
    score = float(request.form.get("score"))
    
    db.execute("INSERT INTO reviews VALUES ( \
                :user_id, :isbn, :review, :score)", \
                {"user_id":user.user_id, "isbn":isbn, "review":review, "score":score})

    book_review = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn":isbn}).fetchone()
    
    reviewer = book_review.reviewers
    avgscore = book_review.avgscore 

    avgscore = (avgscore * float(reviewer) + score) / (float(reviewer) + 1)
    reviewer += 1 

    db.execute("UPDATE books SET \
                reviewers = :reviewer, \
                avgscore = :avgscore \
                WHERE isbn = :isbn", \
                {"reviewer":reviewer, "avgscore":avgscore, "isbn":isbn})

    db.commit()

    return redirect(url_for('account', username=user.username))