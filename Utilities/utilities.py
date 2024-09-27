from flask_mail import Mail
from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token
from datetime import timedelta
import random
from flask_jwt_extended import decode_token
from DataBase.db_config import Token 

#Mail utility
mail = Mail()

def init_mail(app):
    mail.init_app(app)

#JWT utility 
jwt = JWTManager()

def init_jwt(app):
    jwt.init_app(app)

def generate_token(data):
    expires = timedelta(days=30)
    additional_claims = {'sub': data}
    token = create_access_token(
        identity=data, 
        expires_delta=expires,
        additional_claims=additional_claims
    )
    return token

def decode_token_function(token):
    decoded_token = decode_token(token)
    return decoded_token

def color_function():
    color_list = ['A1D6B2','8EACCD','D2E0FB','FF8A8A','73BBA3','FFBF78','FFD18E','6C946F','FCDC94']
    return random.choice(color_list)

def ActiveSession(email):
    token_present = Token.query.filter(Token.email == email).first()
    if token_present:
        return True
    return False


