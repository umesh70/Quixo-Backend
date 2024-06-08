import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flask import Flask
from flask_cors import CORS
from flask_session import Session
from DataBase.db_config import init_db
from Utilities.utilities import init_jwt,init_mail
from Access.access import auth_app

app = Flask(__name__)
CORS(app, origins=['http://localhost:3000'], supports_credentials=True)
app.config['SECRET_KEY'] = '!nS72@wq$u%xY'
app.config['JWT_SECRET_KEY'] = '!lq97IOpPu&VZ'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'work.umesh12@gmail.com'
app.config['MAIL_PASSWORD'] = 'dagxifrxryaeovyl'
app.config['MAIL_DEFAULT_SENDER'] = 'work.umesh12@gmail.com'

app.register_blueprint(blueprint=auth_app, url_prefix='/auth')
init_jwt(app)
init_mail(app)
Session(app)
init_db(app)

if __name__ == '__main__':
    app.run(debug=True)