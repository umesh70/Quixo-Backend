import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import request, jsonify, Blueprint
from DataBase.db_config import db, User, Workspaces
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_jwt_extended import jwt_required
from flask import request, jsonify

Workspace_app = Blueprint('workspace_points', __name__)


@Workspace_app.route('/create_workspace', methods=['POST'])
@jwt_required()
def create_workspace():

    data = request.json
    admin_mail = data['email']
    workspace_name = data['name']
    description = data['description']

    admin_id = get_jwt_identity()
    user = User.query.filter_by(id=admin_id).first()

    if not user:
        return jsonify({'error': 'Invalid user'}), 404

    new_workspace = Workspaces(workspace_name=workspace_name,
                               admin_mail=admin_mail, admin_id=admin_id, description=description)
    db.session.add(new_workspace)
    db.session.commit()
    return jsonify({'message': f'Workspace {workspace_name} created successfully'}), 201


@Workspace_app.route('/get_workspaces', methods=['GET', 'POST'])
@jwt_required()
def get_workspaces():
    # Query the database for all the workspaces
    workspaces = Workspaces.query.order_by(Workspaces.admin_id.asc()).all()
    workspace_list = []
    for workspace in workspaces:
        workspace_data = {
            'id': workspace.workspace_id,
            'workspace_name': workspace.workspace_name,
            'admin_mail': workspace.admin_mail,
            'admin_id': workspace.admin_id,
            'description': workspace.description
        }
# @Workspace_app.route('/del_workspace',methods = ['GET','POST'])
# @jwt_required()
# def del_workspace():
#     data = request.json
#     workspace_id = data['id']

        workspace_list.append(workspace_data)

    return jsonify(workspace_list), 200


@Workspace_app.route('/delete_workspace/<id>', methods=['DELETE'])
@jwt_required()
def delete_workspace(id):

    workspace = Workspaces.query.filter_by(workspace_id=id).first()

    if not workspace:
        return jsonify({'error': 'Workspace does not exist'}), 404

    db.session.delete(workspace)
    db.session.commit()
    return jsonify({'message': 'Workspace deleted successfully'}), 200
