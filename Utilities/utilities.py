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



def generate_token(user_id):
        expires = timedelta(days=1)
        additional_claims = {'sub': user_id}
        token = create_access_token(
            identity=user_id, expires_delta=expires, additional_claims=additional_claims)
        return token