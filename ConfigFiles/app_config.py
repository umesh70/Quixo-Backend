import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from flask_session import Session
from flask_cors import CORS
from datetime import datetime, timedelta
from DataBase.db_config import init_db
from Utilities.utilities import init_jwt,init_mail
from Access.access import auth_app
from Workspace.workspaces import Workspace_app


from DataBase.db_config import User, Workspace,WorkspaceMember  
app = Flask(__name__)

CORS(app, origins=['http://localhost:3000'], supports_credentials=True)

app.config['SECRET_KEY'] = '!nS72@wq$u%xY'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'work.umesh12@gmail.com'
app.config['MAIL_PASSWORD'] = 'dagxifrxryaeovyl'
app.config['MAIL_DEFAULT_SENDER'] = 'work.umesh12@gmail.com'
app.config['SESSION_COOKIE_SECURE'] = True  # For HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_FILE_DIR'] = 'Sessions'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True
Session(app)
init_jwt(app)
init_mail(app)
init_db(app)

app.register_blueprint(blueprint=auth_app, url_prefix='/auth')
app.register_blueprint(blueprint=Workspace_app, url_prefix = '/workspace')

if __name__ == '__main__':
    app.run(debug=True)