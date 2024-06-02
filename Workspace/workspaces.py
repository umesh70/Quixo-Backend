import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ConfigFiles.app_config import create_app
from DataBase.db_config import db, User,Workspaces
from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required
from datetime import timedelta
from flask_mail import Message
from flask_jwt_extended import jwt_required, get_jwt_identity

app, jwt, mail = create_app()


@app.route('/create_workspace',methods=['POST'])
@jwt_required()
def create_workspace():

    data = request.json
    admin_mail = data['email']
    workspace_name = data['name']
    description = data['description']

    admin_id = get_jwt_identity()
    user = User.query.filter_by(id = admin_id).first()
    
    if not user:
        return jsonify({'error': 'Invalid user'}), 404
    
    new_workspace = Workspaces(workspace_name= workspace_name,admin_mail=admin_mail,admin_id= admin_id,description= description)
    db.session.add(new_workspace)
    db.session.commit()
    return jsonify({'message': f'Workspace {workspace_name} created successfully'}), 201