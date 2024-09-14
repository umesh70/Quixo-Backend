from flask_mail import Mail
from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token
from datetime import timedelta
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
# def generateToken(data):
#     expires = timedelta(days=1)
#     additional_claims = {'sub': data}
#     token = create_access_token(
#             identity=data, expires_delta=expires, additional_claims=additional_claims)
#     return token
