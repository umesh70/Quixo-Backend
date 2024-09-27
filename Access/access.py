import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from DataBase.db_config import db, User,Token,WorkspaceToken,WorkspaceMember
from flask import request, jsonify,Blueprint,session
from flask_mail import Message
import random
from  Utilities.utilities import mail , jwt, generate_token, color_function, decode_token
from flask_jwt_extended import jwt_required,get_jwt_identity

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
    
    msg = Message('Verification OTP', recipients=[email])
    msg.body = f'Your OTP for verification is: {otp}'
    
    mail.send(msg)
    print(session)
    return jsonify({'success': 'Account created successfully. Please verify your email to proceed.'}), 201



@auth_app.route('/signup_verification', methods=['POST'])
@jwt_required(optional=True)
def signup_verification():
    data = request.json
    otp = int(data.get('otp'))
    workspace_id = data.get('workspace_id')
    email_token = data.get('token')
    
    if 'user_data' not in session:
        return jsonify({'error': 'No signup session found. Please signup first.'}), 400

    user_data = session.get('user_data')
    stored_otp = user_data.get('otp')  
    email = user_data['email']


    if otp != stored_otp:
        return jsonify({'error': 'Invalid OTP'}), 400

    new_user = User(
        username = user_data['username'],
        password = user_data['password'],
        email = email,
        is_verified = True,
        otp = None,  # Clear OTP after verification
        user_color = color_function()
    )
        
    db.session.add(new_user)
    db.session.commit()

    token = generate_token(new_user.id)
    new_token = Token(
        token = token,
        email = email
    )
    db.session.add(new_token)

    if (workspace_id and email_token):
        if WorkspaceToken.query.filter(token == email_token, email == email, workspace_id == workspace_id):
            workspacemember  = WorkspaceMember(
                workspace_id = workspace_id,
                user_id = new_user.id,
                email = email,
                status = "Member",
            )
            db.session.add(workspacemember)
        else:
            return jsonify({'error':"Invalid user"}), 403
    
    session.pop('user_data', None)
    db.session.commit()
    return jsonify({'success': 'Account created and verified successfully.', 'token' : token, 'id' : new_user.id, 'username' : new_user.username, 'email': new_user.email, 'user_color' : new_user.user_color }), 201
    

@auth_app.route('/login', methods=['POST'])
def login():

    data = request.json
    email = data.get('email')
    password = data.get('password')
    workspace_id = data.get('workspace_id')
    email_token = data.get('token')

    user = User.query.filter_by(email=email).first()

    
    if not user:
        return jsonify({'error': 'User does not exist, please sign up first'}), 404

    if user.password != password:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    token = generate_token(user.id)
    new_token = Token(
        token = token,
        email = email
    )
    db.session.add(new_token)
    
    if (workspace_id and email_token):
        if WorkspaceToken.query.filter(token == email_token, email == email, workspace_id == workspace_id):
            workspacemember  = WorkspaceMember(
                workspace_id = workspace_id,
                user_id = user.id,
                email = email,
                status = "Member",
            )
            db.session.add(workspacemember)
        else:
            return jsonify({'error':"Invalid user"}), 403
    
    
    db.session.commit()
    return jsonify({'success': 'Login successful', 'token': token, 'id':user.id, 'username': user.username, 'email': user.email, 'user_color' : user.user_color}), 200

@auth_app.route('/pw_forget', methods=['POST'])
def pw_forget():
    email = request.json.get('email')
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'User does not exist, please sign up first'}), 404

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


@auth_app.route('/logout', methods=['POST','GET'])
@jwt_required()
def logout():
    print("check")
    try:
        data = request.json
        email = data.get('email')
        print(email)
        if not email:
            return jsonify({"msg": "Email not provided"}), 400
        
        # Check if a token associated with the email exists in the Token table
        token = Token.query.filter_by(email=email).first()
        if token:
            # Delete the token from the Token table
            db.session.delete(token)
            db.session.commit()
            
            return jsonify({"msg": "Successfully logged out"}), 200
        else:
            return jsonify({"msg": "No active session found for this email"}), 404
    except Exception as e:
        return jsonify({"msg": f"An error occurred: {str(e)}"}), 500
        
 