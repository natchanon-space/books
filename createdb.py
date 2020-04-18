from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import csv

# test database
DATABASE_URL = "postgresql://pun:pun@localhost:5432/booksdb"

# app database
# DATABASE_URL = "postgres://ffpjeluuprhaor:34dc7826e49fc4576c2a3373c85283164ecc47a4b08064092331a60cd7fe6bc7@ec2-54-88-130-244.compute-1.amazonaws.com:5432/d2nhtvo1hr1e0j"

engine = create_engine(DATABASE_URL)
db = scoped_session(sessionmaker(bind=engine))

# books table
db.execute("CREATE TABLE books ( \
            isbn VARCHAR PRIMARY KEY, \
            title VARCHAR, \
            author VARCHAR, \
            year INTEGER, \
            reviewers INTEGER, \
            avgscore INTEGER )")
        
# users table
db.execute("CREATE TABLE users ( \
            user_id SERIAL PRIMARY KEY, \
            username VARCHAR NOT NULL, \
            password VARCHAR NOT NULL )")

# reviews table
db.execute("CREATE TABLE reviews ( \
            user_id INTEGER REFERENCES users(user_id), \
            isbn VARCHAR REFERENCES books(isbn), \
            review VARCHAR, \
            score INTEGER NOT NULL )")

with open("books.csv", "r") as books :
    
    reader = csv.DictReader(books)

    for line in reader : 
        db.execute("INSERT INTO books VALUES ( \
                    :isbn, :title, :author, :year, :reviewers, :avgscore)", \
                    {"isbn":line["isbn"], \
                    "title":line["title"], \
                    "author":line["author"], \
                    "year":int(line["year"]), \
                    "reviewers":0, \
                    "avgscore":0 })

db.commit()