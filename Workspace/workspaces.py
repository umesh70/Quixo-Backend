import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ConfigFiles.app_config import create_app
from DataBase.db_config import db, User
from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required
from datetime import timedelta
from flask_mail import Message
import random

app, jwt, mail = create_app()


@app.route('/create_workspace',methods=['POST'])

