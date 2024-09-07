from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from flask_socketio import SocketIO, emit, send
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
socketio = SocketIO(app)

# SQLite database initialization
DATABASE = 'database.db'
def init_db():
    conn = sqlite3.connect(DATABASE)
    conn.execute('CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, name TEXT)')
    conn.close()

# 1. Display "Hello, World!" on the homepage
@app.route('/')
def hello_world():
    return "Hello, World!"

# 2. Static HTML pages navigation
@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

# 3. Dynamic content with URL parameters
@app.route('/user/<name>')
def user(name):
    return f"Hello, {name}!"

# 4. Form that accepts user input and displays it
@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        name = request.form['name']
        return f"Hello, {name}!"
    return render_template('form.html')

# 5. User sessions to store and display user-specific data
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('profile'))
    return render_template('login.html')

@app.route('/profile')
def profile():
    if 'username' in session:
        return f"Hello, {session['username']}!"
    return redirect(url_for('login'))

# 6. File upload and display
app.config['UPLOAD_FOLDER'] = 'uploads/'

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        return f"File uploaded: {file.filename}"
    return render_template('upload.html')

# 7. SQLite database CRUD operations
@app.route('/items')
def items():
    conn = sqlite3.connect(DATABASE)
    items = conn.execute('SELECT * FROM items').fetchall()
    conn.close()
    return render_template('items.html', items=items)

@app.route('/add_item', methods=['POST'])
def add_item():
    conn = sqlite3.connect(DATABASE)
    conn.execute('INSERT INTO items (name) VALUES (?)', (request.form['name'],))
    conn.commit()
    conn.close()
    return redirect(url_for('items'))

@app.route('/delete_item/<int:item_id>')
def delete_item(item_id):
    conn = sqlite3.connect(DATABASE)
    conn.execute('DELETE FROM items WHERE id=?', (item_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('items'))

# 8. User authentication and registration using Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/auth_login', methods=['GET', 'POST'])
def auth_login():
    if request.method == 'POST':
        user = User(request.form['username'])
        login_user(user)
        return redirect(url_for('protected'))
    return render_template('auth_login.html')

@app.route('/protected')
@login_required
def protected():
    return "Logged in!"

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth_login'))

# 9. RESTful API for CRUD operations
books = []

@app.route('/books', methods=['GET'])
def get_books():
    return jsonify(books)

@app.route('/books', methods=['POST'])
def add_book():
    book = request.json
    books.append(book)
    return jsonify(book), 201

@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    book = request.json
    books[book_id] = book
    return jsonify(book)

@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    books.pop(book_id)
    return '', 204

# 10. Error handling for 404 and 500 errors
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# 11. Real-time chat using Flask-SocketIO
@app.route('/chat')
def chat():
    return render_template('chat.html')

@socketio.on('message')
def handle_message(msg):
    send(msg, broadcast=True)

# 12. Real-time data updates using WebSocket
@app.route('/realtime')
def realtime():
    return render_template('realtime.html')

@socketio.on('update_data')
def update_data(data):
    socketio.emit('data_updated', data)

# 13. Notifications using WebSocket
@app.route('/notifications')
def notifications():
    return render_template('notifications.html')

@socketio.on('send_notification')
def send_notification(data):
    emit('notification', data, broadcast=True)

if __name__ == '__main__':
    init_db()  # Initialize the SQLite database
    socketio.run(app, debug=True)
