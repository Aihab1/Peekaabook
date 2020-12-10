import os
from flask import Flask, session, render_template, request, redirect, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests
import json
from datetime import datetime
import random
from quotes import quotes

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
API_KEY = os.getenv("API_KEY")

@app.route("/")
def index():
    if 'username' not in session:
        login_text = "Sign in"
    else:
        login_text = session['username'].capitalize()
        
    quote_number = random.randint(0, len(quotes)-1)
    quote = quotes[quote_number]
    return render_template("index.html", quote = quote, login_text=login_text)

@app.route("/login")
def login():
    if 'username' in session:
        juvenile_fiction = db.execute('SELECT * FROM books WHERE LOWER(genre) = :genre AND imagelink != :imagelink ORDER BY RANDOM() LIMIT 7', {"genre":"juvenile fiction", "imagelink": "NULL"}).fetchall()
        biography_and_autobiography = db.execute('SELECT * FROM books WHERE LOWER(genre) = :genre AND imagelink != :imagelink ORDER BY RANDOM() LIMIT 7', {"genre":"biography & autobiography", "imagelink": "NULL"}).fetchall()
        comics = db.execute('SELECT * FROM books WHERE LOWER(genre) = :genre AND imagelink != :imagelink ORDER BY RANDOM() LIMIT 7', {"genre":"comics & graphic novels", "imagelink": "NULL"}).fetchall()
        drama = db.execute('SELECT * FROM books WHERE LOWER(genre) = :genre AND imagelink != :imagelink ORDER BY RANDOM() LIMIT 7', {"genre":"drama", "imagelink": "NULL"}).fetchall()
        young_adult_fiction = db.execute('SELECT * FROM books WHERE LOWER(genre) = :genre AND imagelink != :imagelink ORDER BY RANDOM() LIMIT 7', {"genre":"young adult fiction", "imagelink": "NULL"}).fetchall()
        children_stories = db.execute('SELECT * FROM books WHERE LOWER(genre) = :genre AND imagelink != :imagelink ORDER BY RANDOM() LIMIT 7', {"genre":"children's stories", "imagelink": "NULL"}).fetchall()
        religion = db.execute('SELECT * FROM books WHERE LOWER(genre) = :genre AND imagelink != :imagelink ORDER BY RANDOM() LIMIT 7', {"genre":"religion", "imagelink": "NULL"}).fetchall()
        business_and_economics = db.execute('SELECT * FROM books WHERE LOWER(genre) = :genre AND imagelink != :imagelink ORDER BY RANDOM() LIMIT 7', {"genre":"business & economics", "imagelink": "NULL"}).fetchall()
        health_and_fitness = db.execute('SELECT * FROM books WHERE LOWER(genre) LIKE :genre AND imagelink != :imagelink ORDER BY RANDOM() LIMIT 7', {"genre":"%health%", "imagelink": "NULL"}).fetchall()
        crime = db.execute('SELECT * FROM books WHERE LOWER(genre) LIKE :genre AND imagelink != :imagelink ORDER BY RANDOM() LIMIT 7', {"genre":"%crime%", "imagelink": "NULL"}).fetchall()
        horror = db.execute('SELECT * FROM books WHERE LOWER(genre) LIKE :genre AND imagelink != :imagelink ORDER BY RANDOM() LIMIT 7', {"genre":"%horror%", "imagelink": "NULL"}).fetchall()
        mystery = db.execute('SELECT * FROM books WHERE LOWER(genre) LIKE :genre AND imagelink != :imagelink ORDER BY RANDOM() LIMIT 7', {"genre":"%mystery%", "imagelink": "NULL"}).fetchall()
        history = db.execute('SELECT * FROM books WHERE LOWER(genre) LIKE :genre AND imagelink != :imagelink ORDER BY RANDOM() LIMIT 7', {"genre":"%history%", "imagelink": "NULL"}).fetchall()
        fantasy = db.execute('SELECT * FROM books WHERE LOWER(genre) LIKE :genre AND imagelink != :imagelink ORDER BY RANDOM() LIMIT 7', {"genre":"%fantasy%", "imagelink": "NULL"}).fetchall()
        poetry = db.execute('SELECT * FROM books WHERE LOWER(genre) LIKE :genre AND imagelink != :imagelink ORDER BY RANDOM() LIMIT 7', {"genre":"%poetry%", "imagelink": "NULL"}).fetchall()
        general_fiction = db.execute('SELECT * FROM books WHERE LOWER(genre) = :genre AND imagelink != :imagelink ORDER BY RANDOM() LIMIT 7', {"genre":"fiction", "imagelink": "NULL"}).fetchall()

        return render_template("dashboard.html", username = session['username'].capitalize(), juvenile_fiction = juvenile_fiction, biography_and_autobiography = biography_and_autobiography, comics = comics, drama = drama, young_adult_fiction = young_adult_fiction, children_stories = children_stories, religion = religion, business_and_economics = business_and_economics, health_and_fitness=health_and_fitness, crime = crime, horror = horror, mystery = mystery, history = history, fantasy = fantasy, poetry = poetry, general_fiction = general_fiction)
    return render_template("login.html")

@app.route("/see_all/<genre>")
def see_all(genre):
    if 'username' in session:
        all_books = db.execute('SELECT * FROM books WHERE LOWER(genre) LIKE :genre', {"genre": "%" + genre + "%"}).fetchall()
        return render_template("seeall.html", all_books = all_books, genre = genre, username = session['username'].capitalize())
    else:
        return redirect(url_for('login'))

@app.route("/dashboard", methods=["GET","POST"])
def dashboard():
    if request.method == 'POST':
        try:
            username = request.form.get("username").lower()
            password = request.form.get("password")
            data = db.execute("SELECT password FROM Users WHERE username = :username", {
                            "username": username}).fetchone()
            if data[0] == password:
                session['username'] = username
                return redirect(url_for('login'))
            return render_template("login.html", errormsg="Incorrect Password. Try Again!")
        except:
            return render_template("login.html", errormsg="No user found. Enter a valid username!")

    else:
        if 'username' in session:
            return redirect(url_for('login'))
        return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route("/register")
def register():
    if 'username' in session:
        return render_template("dashboard.html", username = session['username'].capitalize())
    return render_template("register.html")

@app.route("/registered", methods=["POST"])
def registered():
    # Get form information
    username = request.form.get("username").lower()
    fullname = request.form.get("fullname")
    password = request.form.get("password")
    confirmpassword = request.form.get("confirmpassword")

    try:
        if password == confirmpassword:
            db.execute("INSERT INTO Users (username, fullname, password) VALUES (:username, :fullname, :password)", {
                    "username": username, "fullname": fullname, "password": password})
            db.commit()
            successmsg = "Registered Successfully!"
            return render_template("login.html", successmsg=successmsg)
        return render_template("register.html", errormsg="Passwords didn't match!")
    except:
        return render_template("register.html", errormsg="Username already exists. Try another username!")

@app.route("/search/", methods=["GET"])
def search():
    if 'username' in session:
        mysearch = "%" + request.args.get("search").strip() + "%"
        mybooks = db.execute("SELECT * FROM books WHERE LOWER(title) LIKE :title OR isbn LIKE :isbn OR LOWER(author) LIKE :author ORDER BY title LIMIT 10", {"title": mysearch.lower(), "isbn": mysearch, "author": mysearch.lower()}).fetchall()
        if mybooks != None:
            return render_template("dashboard.html", mybooks = mybooks, username = session['username'].capitalize(), mysearch = mysearch)
        return render_template("dashboard.html", mybooks = ["Sorry, no book found!"], username = session['username'].capitalize())
    else:
        return redirect(url_for('login'))

@app.route("/search/<mysearch>", methods=["GET"])
def see_more(mysearch):
    if 'username' in session:
        mybooks = db.execute("SELECT * FROM books WHERE LOWER(title) LIKE :title OR isbn LIKE :isbn OR LOWER(author) LIKE :author ORDER BY title", {"title": mysearch.lower(), "isbn": mysearch, "author": mysearch.lower()}).fetchall()
        return render_template("seemore.html", mybooks = mybooks, mysearch = mysearch[1:-1], username=session['username'].capitalize())
    return redirect(url_for('login'))

@app.route("/books/<isbn>")
def books(isbn):
    if 'username' in session:
        allreviews = db.execute('SELECT username, review, rating, datetime FROM reviews JOIN books ON reviews.book_id = books.id JOIN Users ON Users.id = reviews.user_id WHERE books.isbn = :isbn', {"isbn": isbn}).fetchall()
        details = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchall()
        reviewed = False
        for areview in allreviews:
            if areview.username == session['username']:
                reviewed = True
                break
            reviewed = False
        
        wishlist_data = db.execute('SELECT username FROM Users JOIN wishlist ON wishlist.user_id = Users.id JOIN books ON wishlist.book_id = books.id WHERE books.isbn = :isbn', {"isbn":isbn}).fetchall()
        wishlisted = False
        for user in wishlist_data:
            if user.username == session['username']:
                wishlisted = True
                break
            wishlisted = False

        #--GOODREADS NO LONGER PROVIDES FREE ACCESS TO ITS API--
        # req1 = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": API_KEY, "isbns": isbn}).json()
        # avg_rating = req1['books'][0]['average_rating']
        # rating_count = req1['books'][0]['work_ratings_count']
        req2 = requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:" + isbn).json()
        try:
            avg_rating = req2['items'][0]['volumeInfo']['averageRating']
            rating_count = req2['items'][0]['volumeInfo']['ratingsCount']
        except:
            avg_rating = None
            rating_count = None

        # req2 = requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:" + isbn).json()
        try:
            description = req2['items'][0]['volumeInfo']['description']
        except:
            description = None
        try:
            previewLink = req2['items'][0]['volumeInfo']['previewLink']
        except:
            previewLink = None
        
        review_count, average_score = db.execute('SELECT COUNT(reviews.rating) AS review_count, AVG(reviews.rating) AS average_score FROM reviews JOIN books ON books.id = reviews.book_id WHERE isbn = :isbn', {"isbn": isbn}).fetchone()
        if average_score != None:
            average_score = float('%.2f'%(average_score))
        else:
            average_score = "/"

        return render_template("book.html", isbn = isbn, details = details[0], allreviews=allreviews, reviewed = reviewed, username = session['username'].capitalize(), avg_rating = avg_rating, rating_count = rating_count, wishlisted = wishlisted, description = description, previewLink = previewLink, review_count=review_count, average_score = average_score)
    else:
        return redirect(url_for('login'))

@app.route("/books/<isbn>/review", methods=["POST"])
def write_review(isbn):
    if request.method == "POST":
        if 'username' in session:
            # now = datetime.now()
            today = datetime.now().date()
            # current_time = now.strftime("%H:%M:%S")
            date = today.strftime('%a, %b %d %Y')
            date_time = date
            rating = request.form['star']
            review = request.form.get('review')
            user_id = db.execute('SELECT id FROM Users WHERE username = :username', {"username": session['username']}).fetchone()[0]
            book_id = db.execute('SELECT id FROM books WHERE isbn = :isbn', {"isbn": isbn}).fetchone()[0]
            db.execute('INSERT INTO reviews (rating, review, book_id, user_id, datetime) VALUES (:rating, :review, :book_id, :user_id, :datetime)', {"rating": rating, "review":review, "book_id": book_id, "user_id": user_id, "datetime": date_time})
            db.commit()

            return redirect(url_for('books', isbn=isbn))
        else:
            return redirect(url_for('login'))

@app.route("/books/<isbn>/review/edit")
def edit_review(isbn):
    if 'username' in session:
        user_id = db.execute('SELECT id FROM Users WHERE username = :username', {"username": session['username']}).fetchone()[0]
        book_id = db.execute('SELECT id FROM books WHERE isbn = :isbn', {"isbn": isbn}).fetchone()[0]
        old_review = db.execute('SELECT review FROM reviews WHERE book_id = :book_id AND user_id = :user_id', {"book_id": book_id, "user_id": user_id}).fetchone()[0]
        return render_template("edit.html", old_review=old_review, isbn=isbn, username = session['username'].capitalize())
    else:
        return redirect(url_for('login'))

@app.route("/books/<isbn>/review/edit/redirect", methods=["POST"])
def edit_review_redirect(isbn):
    if 'username' in session:
        user_id = db.execute('SELECT id FROM Users WHERE username = :username', {"username": session['username']}).fetchone()[0]
        book_id = db.execute('SELECT id FROM books WHERE isbn = :isbn', {"isbn": isbn}).fetchone()[0]
        # now = datetime.now()
        today = datetime.now().date()
        # current_time = now.strftime("%H:%M:%S")
        date = today.strftime('%a, %b %d %Y')
        date_time = date
        rating = request.form['star']
        updated_review = request.form.get('review')
        db.execute('UPDATE reviews SET review = :review, rating = :rating, datetime = :datetime WHERE user_id = :user_id AND book_id = :book_id', {"review": updated_review, "rating": rating, "user_id": user_id, "book_id": book_id, "datetime": date_time})
        db.commit()
        return redirect(url_for('books', isbn=isbn))
    else:
        return redirect(url_for('login'))

@app.route("/books/<isbn>/review/delete")
def delete_review(isbn):
    if 'username' in session:
        user_id = db.execute('SELECT id FROM Users WHERE username = :username', {"username": session['username']}).fetchone()[0]
        book_id = db.execute('SELECT id FROM books WHERE isbn = :isbn', {"isbn": isbn}).fetchone()[0]
        db.execute('DELETE FROM reviews WHERE book_id = :book_id AND user_id = :user_id', {"book_id": book_id, "user_id": user_id})
        db.commit()

        return redirect(url_for('books', isbn=isbn))
    else:
        return redirect(url_for('login'))

@app.route("/profile")
def profile():
    if 'username' in session:
        fullname = db.execute('SELECT fullname FROM Users where username = :username', {"username": session['username']}).fetchone()[0]
        wishlist_data = db.execute('SELECT books.title, wishlist.isbn, books.author, books.imagelink FROM wishlist JOIN books ON wishlist.book_id = books.id JOIN Users ON wishlist.user_id = Users.id WHERE username= :username', {"username": session['username']}).fetchall()
        reviewed_data = db.execute('SELECT title, review, datetime, rating, isbn FROM reviews JOIN books ON reviews.book_id = books.id JOIN Users ON Users.id = reviews.user_id WHERE username=:username', {"username": session['username']}).fetchall()
        return render_template("profile.html", fullname=fullname, wishlist_data = wishlist_data, reviewed_data = reviewed_data, username=session['username'].capitalize())
    else:
        return redirect(url_for('login'))

@app.route("/profile/add-to-wishlist/<isbn>")
def add_to_wishlist(isbn):
    if 'username' in session:
        user_id = db.execute('SELECT id FROM Users WHERE username = :username', {"username": session['username']}).fetchone()[0]
        book_id = db.execute('SELECT id FROM books WHERE isbn = :isbn', {"isbn": isbn}).fetchone()[0]
        db.execute('INSERT INTO wishlist (isbn, user_id, book_id) VALUES (:isbn, :user_id, :book_id)',{"isbn": isbn, "user_id": user_id, "book_id": book_id})
        db.commit()
        return redirect(url_for('books', isbn=isbn))
    return redirect(url_for('login'))

@app.route("/profile/remove-from-wishlist/<isbn>")
def remove_from_wishlist(isbn):
    if 'username' in session:
        user_id = db.execute('SELECT id FROM Users WHERE username = :username', {"username": session['username']}).fetchone()[0]
        book_id = db.execute('SELECT id FROM books WHERE isbn = :isbn', {"isbn": isbn}).fetchone()[0]
        db.execute('DELETE FROM wishlist WHERE isbn = :isbn AND user_id = :user_id AND book_id = :book_id',{"isbn": isbn, "user_id": user_id, "book_id": book_id})
        db.commit()
        return redirect(url_for('books', isbn=isbn))
    return redirect(url_for('login'))

@app.route("/profile/remove-from-wishlist-profile/<isbn>")
def remove_from_wishlist_profile(isbn):
    if 'username' in session:
        user_id = db.execute('SELECT id FROM Users WHERE username = :username', {"username": session['username']}).fetchone()[0]
        book_id = db.execute('SELECT id FROM books WHERE isbn = :isbn', {"isbn": isbn}).fetchone()[0]
        db.execute('DELETE FROM wishlist WHERE isbn = :isbn AND user_id = :user_id AND book_id = :book_id',{"isbn": isbn, "user_id": user_id, "book_id": book_id})
        db.commit()
        return redirect(url_for('profile'))
    return redirect(url_for('login'))

@app.route("/api/<isbn>")
def get_api(isbn):
    data = db.execute('SELECT title, author, year, isbn, COUNT(reviews.rating) AS review_count, AVG(reviews.rating) AS average_score FROM books JOIN reviews ON books.id = reviews.book_id WHERE isbn = :isbn GROUP BY title, author, year, isbn', {"isbn": isbn}).fetchall()

    req2 = requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:" + isbn).json()
    try:
        genres = req2['items'][0]['volumeInfo']['categories']
    except:
        genres = None
        
    if len(data) != 1:
        return jsonify({"Error": "ISBN not in database!"}), 422

    result_data = dict(data[0].items())
    result_data['average_score'] = float('%.2f'%(result_data['average_score']))
    if genres != None:
        if 'genre' not in result_data:
            result_data['genre'] = genres[0]

    return jsonify(result_data)
