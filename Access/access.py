from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_cors import CORS, cross_origin
import random
from datetime import datetime
from functools import wraps
from flask_session import Session
from flask_jwt_extended import JWTManager,create_access_token
from datetime import timedelta

app = Flask(__name__)

CORS(app, origins=['http://localhost:3000'], supports_credentials=True)
jwt = JWTManager(app)
app.config['SECRET_KEY'] = '!nS72@wq$u%xY'
app.config['JWT_SECRET_KEY'] = '!lq97IOpPu&VZ'


# SQLAlchemy configuration (if using)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Change to your SMTP server
app.config['MAIL_PORT'] = 587  # Change to your SMTP port
app.config['MAIL_USE_TLS'] = True  # Enable TLS
# Change to your email address
app.config['MAIL_USERNAME'] = 'work.umesh12@gmail.com'
# Change to your email password
app.config['MAIL_PASSWORD'] = 'dagxifrxryaeovyl'
# Change to your email address
app.config['MAIL_DEFAULT_SENDER'] = 'work.umesh12@gmail.com'

# Session configuration
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = False
app.config['SESSION_TYPE'] = 'filesystem'

mail = Mail(app)

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    otp = db.Column(db.Integer)

# Create the database tables
with app.app_context():
    db.create_all()

Session(app)

def generate_token(user_id):
    with app.app_context():
        expires = timedelta(days=1)
        additional_claims = {'sub': user_id}
        token = create_access_token(identity=user_id, expires_delta=expires, additional_claims=additional_claims)
        return token



# signup
@app.route('/signup', methods=['POST'])
@cross_origin()
def signup():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not username or not password or not email:
        return jsonify({'error': 'Username, password, and email are required'}), 400

    # Check for existing usernames and emails
    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        return jsonify({'error': 'User already exists'}), 400

    # Generate a unique OTP
    otp = ''.join(random.choices('0123456789', k=6))

    new_user = User(username=data['username'],
                    password=password,
                    email=data['email'],
                    is_verified=False,
                    otp=otp)
    db.session.add(new_user)
    db.session.commit()

    # Send email with OTP
    msg = Message('Verification OTP', recipients=[email])
    msg.body = f'Your OTP for verification is: {otp}'
    mail.send(msg)

    token = generate_token(new_user.id)
    return jsonify({'success': 'Account created successfully. Please verify your email to proceed.','token':token}), 201


@app.route('/signup_verification', methods=['POST'])
def signup_verification():
    data = request.json
    email = data.get('email')
    otp = data.get('otp')
    print(otp)
    if not email or not otp:
        return jsonify({'error': 'OTP is required'}), 401

    # Fetch user by email securely using prepared statements
    user = User.query.filter_by(email=email).first()
    print(user.otp)
    if not user:
        return jsonify({'error': 'Invalid email'}), 402

    if user.otp != otp:
        return jsonify({'error': 'Invalid OTP'}), 403

    access_token = generate_token(user.id)
    print(access_token)

    # Clear OTP after successful verification
    user.otp = None

    user.verified = True
    db.session.commit()

    return jsonify({'success': 'Email verified successfully'}), 200


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email, password=password).first()
    token = generate_token(user.id)
    if user:
        return jsonify({'success': 'Login successful','token':token}) ,200
    else:
        return jsonify({'error': 'Invalid email or password'}), 401


@app.route('/pw_forget', methods=['POST'])
@cross_origin()
def pw_forget():
    email = request.json.get('email')
    if not email:
        return jsonify({'error': 'Email is required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Generate a unique OTP for password reset
    otp = ''.join(random.choices('0123456789', k=6))
    user.otp = otp
    db.session.commit()

    # Send email with OTP for password reset
    msg = Message('Password Reset OTP', recipients=[email])
    msg.body = f'Your OTP for password reset is: {otp}'
    mail.send(msg)

    return jsonify({'success': 'Password reset OTP sent successfully'}), 200


@app.route('/pw_reset', methods=['POST'])
@cross_origin()
def pw_reset():
    email = request.json.get('email')
    otp = request.json.get('otp')
    new_password = request.json.get('new_password')
    print(otp)

    if not email or not otp or not new_password:
        return jsonify({'error': 'OTP, and new password are required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    print(user.otp)

    if user.otp != otp:
        return jsonify({'error': 'Invalid OTP'}), 401

    # Reset password
    user.password = new_password
    user.otp = None
    db.session.commit()

    return jsonify({'success': 'Password reset successful'}), 200


@app.route('/protected', methods=['GET'])
def protected():
    token = request.headers.get('Authorization')
    if token.startswith('Bearer '):
        token = token[7:]

    try:
        data = jwt.decode(
            token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return jsonify({'user_id': data['sub']})
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token'}), 401


if __name__ == '__main__':
    generate_token(1)
    app.run(debug=True)
