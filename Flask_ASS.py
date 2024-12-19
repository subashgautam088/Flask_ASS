# 2. Build a Flask app with static HTML pages and navigate between them.

from flask import Flask, render_template, request,session, redirect, url_for,send_from_directory
import os
app = Flask(__name__)

# Define Route for home page
@app.route("/home")
def home():
    return render_template("home.html")

# Define Route for about page
@app.route("/about")
def about():
    return render_template("about.html")


#-------------------------------------------------------------------------

# 3. Develop a Flask app that uses URL parameters to display dynamic content.

# Define the route with numeric URL parameter
@app.route("/url_parameter/<int:number>")
def url_parameter(number):
    result = number ** 2
    return f"The square of {number} is {result}"
    

@app.route("/greet/<name>")
def greet(name):
    return f"Hello, {name} Welcome to our flask app"


#-------------------------------------------------------------------------

# 4. Create a Flask app with a form that accepts user input and displays it.
@app.route("/form")
def form():
    return render_template("form.html")

# Route to handle form submission and display results
@app.route('/submit', methods=['POST'])
def submit():
    user_input = request.form.get("user_input")
    return render_template('result.html', user_input=user_input)    

#-------------------------------------------------------------------------
# 5. Implement user sessions in a Flask app to store and display user-specific data.

# Set a secret key for the session
app.secret_key = 'pwskills'

@app.route('/sessions')
def sessions():
    # Get the username from the form
    return render_template("sessions.html")

@app.route('/flask_login', methods=['POST'])
def flask_login():
    username = request.form.get("username")
    
    # Store the username in the session
    session['username'] = username
    
    return redirect(url_for('flask_dashboard'))

@app.route('/flask_dashboard')
def flask_dashboard():
    # Check if user is logged in
    if 'username' in session:
        username = session['username']
        return render_template('dashboard.html', username=username)
    else:
        return redirect(url_for('sessions'))
    
@app.route('/flask_logout')
def flask_logout():
    # Remove the user from the session
    session.pop('username', None)
    return redirect(url_for('sessions'))



#-------------------------------------------------------------------------
# 6. Build a Flask app that allows users to upload files and display them on the website.

UPLOAD_FOLDER = 'uploaded_file'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/file_upload")
def file_upload():
    # Display the upload form
    return render_template('file_upload.html')

@app.route("/upload", methods=["POST"])
def upload_file():
    if 'file' not in request.files:
        return "No file part in the request", 400
    
    file = request.files['file']
    
    # If no file is selected
    if file.filename == '':
        return "No selected file", 400
    
    # Save the file to the upload folder
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    
    return redirect(url_for("display_files"))

@app.route('/uploaded_file/<filename>')
def uploaded_file(filename):
    # Serve the uploaded file
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/display')
def display_files():
    # Get the list of uploaded files
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template("display.html", files=files)

#-------------------------------------------------------------------------

# 7. Integrate a SQLite database with Flask to perform CRUD operations on a list of items.
import sqlite3

# SQLite database file
DATABASE = 'items.db'

# Initialize database
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS items (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL
                     )''')
    conn.commit()
    conn.close()

# Route: Home - Display all items
@app.route('/sql_file')
def sql_file():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM items')
    items = cursor.fetchall()
    conn.close()
    return render_template('sql_file.html', items=items)

# Route: Add item - Form
@app.route('/add', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        name = request.form['name']
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO items (name) VALUES (?)', (name,))
        conn.commit()
        conn.close()
        return redirect(url_for('sql_file'))
    return render_template('add_item.html')

# Route: Update item - Form
@app.route('/update/<int:item_id>', methods=['GET', 'POST'])
def update_item(item_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    if request.method == 'POST':
        new_name = request.form['name']
        cursor.execute('UPDATE items SET name = ? WHERE id = ?', (new_name, item_id))
        conn.commit()
        conn.close()
        return redirect(url_for('sql_file'))
    else:
        cursor.execute('SELECT * FROM items WHERE id = ?', (item_id,))
        item = cursor.fetchone()
        conn.close()
        return render_template('update_item.html', item=item)

# Route: Delete item
@app.route('/delete/<int:item_id>')
def delete_item(item_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM items WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('sql_file'))

#-------------------------------------------------------------------------
# 8. Implement user authentication and registration in a Flask app using Flask-Login.

from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app.secret_key = 'supersecretkey'

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# SQLite database file
DATABASE = 'users.db'

# Initialize database
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL
                     )''')
    conn.commit()
    conn.close()

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

    @staticmethod
    def get(user_id):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        if user:
            return User(user[0], user[1])
        return None

# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Route: Homepage
@app.route('/flask_app')
def flask_app():
    return render_template('flask_app.html', current_user=current_user)

# Route: Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            conn.commit()
            flash('Registration successful. Please log in.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists.')
        finally:
            conn.close()

    return render_template('register.html')

# Route: Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            user_obj = User(user[0], user[1])
            login_user(user_obj)
            flash('Logged in successfully.')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.')

    return render_template('login.html')

# Route: Dashboard (Protected)
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('flask_dashboard.html', username=current_user.username)

# Route: Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.')
    return redirect(url_for('flask_app'))


#-------------------------------------------------------------------------
# 9. Create a RESTful API using Flask to perform CRUD operations on resources like books or movies.
from flask import  jsonify, abort
from flask_sqlalchemy import SQLAlchemy


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Model for the Book resource
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    author = db.Column(db.String(80), nullable=False)
    year = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {"id": self.id, "title": self.title, "author": self.author, "year": self.year}

# Initialize the database
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensures tables are created
    app.run(debug=True)


# Routes for CRUD operations

# GET all books
@app.route('/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    return jsonify([book.to_dict() for book in books]), 200

# GET a single book by ID
@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = Book.query.get(book_id)
    if book is None:
        abort(404, description="Book not found")
    return jsonify(book.to_dict()), 200

# POST a new book
@app.route('/books', methods=['POST'])
def create_book():
    if not request.json or not all(key in request.json for key in ['title', 'author', 'year']):
        abort(400, description="Invalid input")
    new_book = Book(
        title=request.json['title'],
        author=request.json['author'],
        year=request.json['year']
    )
    db.session.add(new_book)
    db.session.commit()
    return jsonify(new_book.to_dict()), 201

# PUT (update) an existing book by ID
@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    book = Book.query.get(book_id)
    if book is None:
        abort(404, description="Book not found")
    if not request.json:
        abort(400, description="Invalid input")
    book.title = request.json.get('title', book.title)
    book.author = request.json.get('author', book.author)
    book.year = request.json.get('year', book.year)
    db.session.commit()
    return jsonify(book.to_dict()), 200

# DELETE a book by ID
@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = Book.query.get(book_id)
    if book is None:
        abort(404, description="Book not found")
    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": "Book deleted"}), 200

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": str(error)}), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": str(error)}), 400



# 10. Design a Flask app with proper error handling for 404 and 500 errors.

# Home route
@app.route("/home1")
def home1():
    return "<h1>Welcome to the Flask App</h1><p>Try accessing a non-existent page to see custom error handling.</p>"

# About route
@app.route("/about1")
def about1():
    return "<h1>About Page</h1><p>This is an example Flask app with error handling.</p>"

# Error handler for 404 (Page Not Found)
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# Error handler for 500 (Internal Server Error)
@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500


#--------------------------------------------------------------
# 11. Create a real-time chat application using Flask-SocketIO.
from flask_socketio import SocketIO, send

# Initialize Flask app and Flask-SocketIO

app.config['SECRET_KEY'] = 'pwskills'
socketio = SocketIO(app)

# Serve the chat interface
@app.route("/chat_real")
def chat_real():
    return render_template("chat_real.html")

# Handle messages sent from clients
@socketio.on('message')
def handle_message(msg):
    print(f"Message received: {msg}")
    # Broadcast the message to all connected clients
    send(msg, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, debug=True)





# Initialize database before running the app
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0',debug=True)

    
    
