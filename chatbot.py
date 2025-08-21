from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import google.generativeai as genai

app = Flask(__name__)
app.secret_key = "supersecret"

# MongoDB Connection
app.config["MONGO_URI"] = "mongodb://localhost:27017/LibraryDB"
mongo = PyMongo(app)

# Gemini API Key
genai.configure(api_key="AIzaSyDGOSRXWiBBTWmR4Cff32GuzEJIeF6XNRo")   # 🔹 Replace with your actual key


# Home (SignUp / Login)
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        if "signup" in request.form:   # Signup
            username = request.form["username"]
            email = request.form["email"]

            # Check if user already exists
            existing_user = mongo.db.Users.find_one({"Email": email})
            if existing_user:
                flash("A user with this email already exists. Please use a different email or login.", "error")
                return render_template("home.html")

            # Auto-generate new User_id
            last = mongo.db.Users.find_one(sort=[("User_id", -1)])
            new_id = 1 if not last else last["User_id"] + 1

            mongo.db.Users.insert_one({
                "User_id": new_id,
                "Username": username,
                "Email": email,
                "borrowed_books": []
            })

            session["user_id"] = new_id
            session["username"] = username
            flash(f"Welcome {username}! Your account has been created successfully. Your User ID is: {new_id}", "success")
            return redirect(url_for("books"))

        elif "login" in request.form:  # Login
            try:
                user_id = int(request.form["user_id"])
                user = mongo.db.Users.find_one({"User_id": user_id})
                if user:
                    session["user_id"] = user_id
                    session["username"] = user["Username"]
                    flash(f"Welcome back, {user['Username']}!", "success")
                    return redirect(url_for("books"))
                else:
                    flash("Invalid User ID. Please check your ID and try again.", "error")
            except ValueError:
                flash("Please enter a valid User ID (numbers only).", "error")

    return render_template("home.html")


# View Books
@app.route("/books")
def books():
    if "user_id" not in session:
        return redirect(url_for("home"))

    books = list(mongo.db.Books.find())
    return render_template("books.html", books=books)

# Book detail
@app.route("/books/<int:book_id>")
def book_detail(book_id: int):
    if "user_id" not in session:
        return redirect(url_for("home"))

    book = mongo.db.Books.find_one({"Book_id": book_id})
    if not book:
        flash("Book not found.", "error")
        return redirect(url_for("books"))

    description = book.get("Description")
    if not description:
        try:
            model = genai.GenerativeModel("gemini-2.5-flash")
            prompt = f"""
            You are helping a library show a brief description for a book.
            Write a concise, engaging 3-4 sentence description suitable for a library catalog.
            Avoid spoilers. Focus on premise, themes, and why it appeals to readers.

            Title: {book.get('Title', '')}
            Authors: {', '.join(book.get('Authors', []))}
            Genres: {', '.join(book.get('Genres', []))}
            """
            result = model.generate_content(prompt)
            description = (result.text or "").strip()
            if description:
                mongo.db.Books.update_one({"Book_id": book_id}, {"$set": {"Description": description}})
        except Exception:
            # Fail softly if AI is unavailable
            description = None

    return render_template("book_detail.html", book=book, description=description)

# Add Book
@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    if "user_id" not in session:
        return redirect(url_for("home"))

    if request.method == "POST":
        title = request.form["title"].strip()
        authors = [a.strip() for a in request.form["authors"].split(",") if a.strip()]
        genres = [g.strip() for g in request.form["genres"].split(",") if g.strip()]
        
        try:
            copies = int(request.form["copies"])
            if copies <= 0:
                flash("Number of copies must be greater than 0.", "error")
                return render_template("add_book.html")
        except ValueError:
            flash("Please enter a valid number for copies.", "error")
            return render_template("add_book.html")

        if not title or not authors or not genres:
            flash("Please fill in all required fields.", "error")
            return render_template("add_book.html")

        # Auto-generate Book_id
        last = mongo.db.Books.find_one(sort=[("Book_id", -1)])
        new_book_id = 1 if not last else last["Book_id"] + 1

        mongo.db.Books.insert_one({
            "Book_id": new_book_id,
            "Title": title,
            "Authors": authors,
            "Genres": genres,
            "Total_copies": copies,
            "Available_copies": copies
        })
        
        flash(f"Book '{title}' has been added successfully to the library!", "success")
        return redirect(url_for("books"))

    return render_template("add_book.html")

# Borrow Book
@app.route("/borrow", methods=["GET", "POST"])
def borrow_book():
    if "user_id" not in session:
        return redirect(url_for("home"))

    books = list(mongo.db.Books.find({'Available_copies': {'$gt': 0}}))

    if request.method == "POST":
        try:
            book_id = int(request.form["book_id"])
            book = mongo.db.Books.find_one({"Book_id": book_id})

            if book and book["Available_copies"] > 0:
                # Reduce available copies
                mongo.db.Books.update_one({"Book_id": book_id}, {"$inc": {"Available_copies": -1}})
                # Track borrowed book for user
                mongo.db.Users.update_one(
                    {"User_id": session["user_id"]},
                    {"$push": {"borrowed_books": {"Book_id": book["Book_id"], "Title": book["Title"]}}}
                )
                flash(f"Successfully borrowed '{book['Title']}'! Please return it within 14 days.", "success")
                return redirect(url_for("books"))
            else:
                flash("Sorry, this book is no longer available for borrowing.", "error")
        except ValueError:
            flash("Invalid book selection. Please try again.", "error")

    return render_template("borrow_book.html", books=books)

# Return Book
@app.route("/return", methods=["GET", "POST"])
def return_book():
    if "user_id" not in session:
        return redirect(url_for("home"))

    # Build normalized borrowed list for the current user
    user = mongo.db.Users.find_one({"User_id": session["user_id"]})
    if not user:
        flash("User not found.", "error")
        return redirect(url_for("home"))

    normalized_borrowed = []
    for borrowed_item in user.get("borrowed_books", []):
        if isinstance(borrowed_item, dict) and "Book_id" in borrowed_item and borrowed_item["Book_id"] is not None:
            # Ensure title is present
            if not borrowed_item.get("Title"):
                book_doc = mongo.db.Books.find_one({"Book_id": int(borrowed_item["Book_id"])})
                title = book_doc["Title"] if book_doc else "Unknown"
                normalized_borrowed.append({"Book_id": int(borrowed_item["Book_id"]), "Title": title})
            else:
                normalized_borrowed.append({"Book_id": int(borrowed_item["Book_id"]), "Title": borrowed_item["Title"]})
        else:
            # Fallback by title-only records
            title = borrowed_item if isinstance(borrowed_item, str) else str(borrowed_item)
            book_doc = mongo.db.Books.find_one({"Title": title})
            if book_doc:
                normalized_borrowed.append({"Book_id": int(book_doc["Book_id"]), "Title": title})
            else:
                # Keep entry with None id to at least display
                normalized_borrowed.append({"Book_id": None, "Title": title})

    if request.method == "POST":
        try:
            book_id = int(request.form.get("book_id", "").strip())
        except ValueError:
            flash("Invalid selection. Please try again.", "error")
            return render_template("return_book.html", borrowed=normalized_borrowed)

        book = mongo.db.Books.find_one({"Book_id": book_id})
        if not book:
            flash("Selected book was not found.", "error")
            return render_template("return_book.html", borrowed=normalized_borrowed)

        # Verify the user actually has this book borrowed
        has_borrowed = any((item.get("Book_id") == book_id) for item in normalized_borrowed)
        if not has_borrowed:
            flash("This book is not in your borrowed list.", "error")
            return render_template("return_book.html", borrowed=normalized_borrowed)

        # Increment available copies
        mongo.db.Books.update_one({"Book_id": book_id}, {"$inc": {"Available_copies": 1}})

        # Remove from user's borrowed list (support both new dict format and legacy string format)
        mongo.db.Users.update_one(
            {"User_id": session["user_id"]},
            {"$pull": {"borrowed_books": {"Book_id": book_id}}}
        )
        mongo.db.Users.update_one(
            {"User_id": session["user_id"]},
            {"$pull": {"borrowed_books": book["Title"]}}
        )

        flash(f"Successfully returned '{book['Title']}'. Thank you!", "success")
        return redirect(url_for("my_collection"))

    return render_template("return_book.html", borrowed=normalized_borrowed)

# Chatbot (AI Librarian)
@app.route("/chat", methods=["GET", "POST"])
def chat():
    if "user_id" not in session:
        return redirect(url_for("home"))

    response_text = None

    if request.method == "POST":
        user_message = request.form["message"].strip()
        
        if not user_message:
            flash("Please enter a message to chat with the AI librarian.", "error")
            return render_template("chat.html")

        try:
            # Fetch books from DB (for context)
            books = list(mongo.db.Books.find({}, {"_id": 0, "Title": 1, "Authors": 1, "Genres": 1}))

            # Format context for Gemini
            book_context = "\n".join(
                [f"- {b['Title']} by {', '.join(b['Authors'])} (Genres: {', '.join(b['Genres'])})" for b in books]
            )

            # Ask Gemini
            model = genai.GenerativeModel("gemini-2.5-flash")
            prompt = f"""
            You are a helpful and friendly librarian assistant for a NoSQL Library system.
            
            Available books in the library:
            {book_context}

            User asked: {user_message}
            
            Please provide a helpful, friendly response. If the user is asking for book recommendations, 
            suggest books from the available library collection. Be conversational and encouraging.
            Keep your response concise but informative.
            """
            result = model.generate_content(prompt)
            response_text = result.text
            
        except Exception as e:
            flash("Sorry, I'm having trouble connecting to the AI service right now. Please try again later.", "error")
            response_text = "I apologize, but I'm experiencing technical difficulties at the moment. Please try again later or contact the library staff for assistance."

    return render_template("chat.html", response=response_text)


# Logout
@app.route("/logout")
def logout():
    if "username" in session:
        username = session["username"]
        session.clear()
        flash(f"Goodbye, {username}! You have been successfully logged out.", "success")
    else:
        session.clear()
        flash("You have been logged out.", "success")
    return redirect(url_for("home"))


# Profile page
@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("home"))

    user = mongo.db.Users.find_one({"User_id": session["user_id"]})
    if not user:
        flash("User not found.", "error")
        return redirect(url_for("home"))

    # Normalize borrowed items to include Book_id and Title when possible
    normalized_borrowed = []
    for borrowed_item in user.get("borrowed_books", []):
        if isinstance(borrowed_item, dict) and "Book_id" in borrowed_item:
            normalized_borrowed.append(borrowed_item)
        else:
            # Backward compatibility: borrowed_item is likely a title string
            title = borrowed_item if isinstance(borrowed_item, str) else str(borrowed_item)
            book_doc = mongo.db.Books.find_one({"Title": title})
            if book_doc:
                normalized_borrowed.append({"Book_id": book_doc.get("Book_id"), "Title": title})
            else:
                normalized_borrowed.append({"Book_id": None, "Title": title})

    borrowed_count = len(normalized_borrowed)
    return render_template("profile.html", user=user, borrowed_books=normalized_borrowed, borrowed_count=borrowed_count)


# My Collection (books borrowed by the current user)
@app.route("/my_collection")
def my_collection():
    if "user_id" not in session:
        return redirect(url_for("home"))

    user = mongo.db.Users.find_one({"User_id": session["user_id"]})
    if not user:
        flash("User not found.", "error")
        return redirect(url_for("home"))

    borrowed_items = user.get("borrowed_books", [])
    books_to_show = []
    for item in borrowed_items:
        if isinstance(item, dict) and "Book_id" in item and item["Book_id"] is not None:
            book_doc = mongo.db.Books.find_one({"Book_id": int(item["Book_id"])})
            if book_doc:
                books_to_show.append(book_doc)
            continue
        # Fallback by title
        title = item.get("Title") if isinstance(item, dict) else (item if isinstance(item, str) else None)
        if title:
            book_doc = mongo.db.Books.find_one({"Title": title})
            if book_doc:
                books_to_show.append(book_doc)

    return render_template("my_collection.html", books=books_to_show)


if __name__ == "__main__":
    app.run(debug=True)
