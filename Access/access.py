from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = '\xf0?a\x9a\\\xff\xd4;\x0c\xcbHi'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Change to your SMTP server
app.config['MAIL_PORT'] = 587  # Change to your SMTP port
app.config['MAIL_USE_TLS'] = True  # Enable TLS
app.config['MAIL_USERNAME'] = 'work.umesh12@gmail.com'  # Change to your email address
app.config['MAIL_PASSWORD'] = 'tuJUgiiy:Q6Phhy'  # Change to your email password
app.config['MAIL_DEFAULT_SENDER'] = 'work.umesh12@gmail.com'  # Change to your email address

mail = Mail(app)

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)

# Create the database tables
with app.app_context():
    db.create_all()

# signup
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not username or not password or not email:
        return jsonify({'error': 'Username, password, and email are required'}), 400

    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        return jsonify({'error': 'User already exists'}), 400
    
    # Generate OTP
    otp = ''.join(random.choices('0123456789', k=6))

    # Store user details temporarily in session
    session['temp_user'] = {'username': username, 'password': password, 'email': email, 'otp': otp}

    # Send email with OTP
    msg = Message('Verification OTP', recipients=[email])
    msg.body = f'Your OTP for verification is: {otp}'
    mail.send(msg)

    return jsonify({'success': 'OTP generated successfully and sent to email', 'otp': otp}), 200

@app.route('/verify', methods=['POST'])
def verify():
    data = request.json
    email = data.get('email')
    otp = data.get('otp')

    if not email or not otp:
        return jsonify({'error': 'Email and OTP are required'}), 400

    temp_user = session.get('temp_user')
    if not temp_user:
        return jsonify({'error': 'User details not found'}), 404

    if temp_user['email'] != email or temp_user['otp'] != otp:
        return jsonify({'error': 'Invalid email or OTP'}), 400

    new_user = User(username=temp_user['username'], password=temp_user['password'], email=temp_user['email'])
    db.session.add(new_user)
    db.session.commit()

    session.pop('temp_user')

    return jsonify({'success': 'User registered successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)
