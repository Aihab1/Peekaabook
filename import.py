import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import os
import requests
# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# myfile = open('books.csv')
# reader = csv.reader(myfile)

# for isbn, title, author, year in reader:
#     print(isbn, title, author, year)
#     db.execute('INSERT INTO Books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)', {"isbn": isbn, "title": title, "author": author, "year": year})

mybooks = db.execute("SELECT isbn FROM books").fetchall()
i=1
for isbn in mybooks:
    try:
        req = requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:" + isbn[0]).json()
        # imageLink = (req['items'][0]['volumeInfo']['imageLinks']['thumbnail'])
        genre = req['items'][0]['volumeInfo']['categories'][0]
        db.execute("UPDATE books SET genre = :genre WHERE isbn = :isbn", {"genre": genre, "isbn": isbn[0]})
        print(i, genre)
    except:
        print(i)
    i = i+1
db.commit()