import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from DataBase.db_config import db, User
from flask import request, jsonify,Blueprint,session
from flask_mail import Message
import random
from  Utilities.utilities import mail , jwt, generate_token


auth_app = Blueprint('auth',__name__)

@auth_app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not username or not password or not email:
        return jsonify({'error': 'Username, password, and email are required'}), 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({'error': 'Username or email already exists'}), 409

    otp = random.randint(111111, 999999)
    session['user_data'] = {
        'username': username,
        'password': password,
        'email': email,
        'otp': otp
    }
    # new_user = User(username=username, password=password, email=email, is_verified=False, otp=otp)
    # db.session.add(new_user)
    # db.session.commit()

    msg = Message('Verification OTP', recipients=[email])
    msg.body = f'Your OTP for verification is: {otp}'
    mail.send(msg)

    # token = generate_token(see)
    return jsonify({'success': 'Account created successfully. Please verify your email to proceed.'}), 201



@auth_app.route('/signup_verification', methods=['POST'])
def signup_verification():
    data = request.json
    otp = int(data.get('otp'))
    print(session.get('user_data'))
    if 'user_data' not in session:
        return jsonify({'error': 'No signup session found. Please signup first.'}), 400

    user_data = session.get('user_data')
    stored_otp = user_data.get('otp')
    

    if otp != stored_otp:
        return jsonify({'error': 'Invalid OTP'}), 400

    new_user = User(
        username=user_data['username'],
        password=user_data['password'],
        email=user_data['email'],
        is_verified=True,
        otp=None  # Clear OTP after verification
    )
    db.session.add(new_user)
    db.session.commit()

    session.pop('user_data', None)

    token = generate_token(new_user.id)
    return jsonify({'success': 'Account created and verified successfully.', 'token': token}), 201
    
@auth_app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({'error': 'User does not exist, please sign up first'}), 404

    if user.password != password:
        return jsonify({'error': 'Invalid credentials'}), 401

    token = generate_token(user.id)
    return jsonify({'success': 'Login successful', 'token': token, 'username': user.username, 'email': user.email}), 200

@auth_app.route('/pw_forget', methods=['POST'])
def pw_forget():
    email = request.json.get('email')
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    otp = random.randint(100000, 999999)
    user.otp = otp
    db.session.commit()

    msg = Message('Password Reset OTP', recipients=[email])
    msg.body = f'Your OTP for password reset is: {otp}'
    mail.send(msg)

    return jsonify({'success': 'Password reset OTP sent successfully'}), 200



@auth_app.route('/pw_reset', methods=['POST'])
def pw_reset():
    data = request.json
    email = data.get('email')
    otp = int(data.get('otp'))
    new_password = data.get('new_password')

    user = User.query.filter_by(email=email).first()
    if not user or user.otp != otp:
        return jsonify({'error': 'Invalid email or OTP'}), 400

    user.password = new_password
    user.otp = None  # Clear the OTP after use
    db.session.commit()

    return jsonify({'success': 'Password reset successful'}), 200

@auth_app.route('/protected', methods=['GET'])
def protected():
    token = request.headers.get('Authorization')
    if token.startswith('Bearer '):
        token = token[7:]

    try:
        data = jwt.decode(
            token, auth_app.config['SECRET_KEY'], algorithms=['HS256'])
        return jsonify({'user_id': data['sub']})
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token'}), 401