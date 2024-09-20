import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import request, jsonify, Blueprint, url_for,redirect
from DataBase.db_config import db, User, Workspace,WorkspaceMember
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_jwt_extended import jwt_required
from flask import request, jsonify
import re
from Utilities.utilities import generate_token,mail
from flask_mail import Message
from sqlalchemy.exc import IntegrityError
from Access.access import ActiveSession,signup,login


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
    new_workspace = Workspace(workspace_name=workspace_name,
                               admin_mail=admin_mail, admin_id=admin_id, description=description)
    db.session.add(new_workspace)
    db.session.commit()
    return jsonify({'message': f'Workspace {workspace_name} created successfully'}), 201





@Workspace_app.route('/get_user_workspaces/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_workspaces(user_id):
    # Query workspaces created by the user (where user is admin)
    created_workspaces = Workspace.query.filter_by(admin_id=user_id).all()
    print(created_workspaces)

    # Query workspaces the user is invited to
    invited_workspaces = (
        Workspace.query
        .join(WorkspaceMember)
        .filter(WorkspaceMember.user_id == user_id)
        .filter(Workspace.admin_id != user_id)
        .all()
    )
    print(invited_workspaces)

    # Function to convert workspace object to dictionary
    def workspace_to_dict(workspace):
        return {
            'workspace_id': workspace.workspace_id,
            'workspace_name': workspace.workspace_name,
            'description': workspace.description,
            'admin_mail': workspace.admin_mail
        }
    
    # Convert query results to list of dictionaries
    created_workspaces_list = [workspace_to_dict(w) for w in created_workspaces]
    invited_workspaces_list = [workspace_to_dict(w) for w in invited_workspaces]
    
    return jsonify({
        'created_workspaces': created_workspaces_list,
        'invited_workspaces': invited_workspaces_list
    })

def get_workspaces():
    # Query the database for all the workspaces
    workspaces = Workspace.query.order_by(Workspace.admin_id.asc()).all()
    workspace_list = []
    for workspace in workspaces:
        workspace_data = {
            'id': workspace.workspace_id,
            'workspace_name': workspace.workspace_name,
            'admin_mail': workspace.admin_mail,
            'admin_id': workspace.admin_id,
            'description': workspace.description
        }
        workspace_list.append(workspace_data)

    return jsonify(workspace_list), 200


@Workspace_app.route('/delete_workspace/<id>', methods=['DELETE'])
@jwt_required()
def delete_workspace(id):

    workspace = Workspace.query.filter_by(workspace_id=id).first()

    if not workspace:
        return jsonify({'error': 'Workspace does not exist'}), 404

    db.session.delete(workspace)
    db.session.commit()
    return jsonify({'message': 'Workspace deleted successfully'}), 200


"""
Endpoint for sending an invite via email(Send invite link to their email)
"""

@Workspace_app.route('/add_member/<workspace_id>',methods = ['POST'])
@jwt_required()
def add_member(workspace_id):
    currentUser = get_jwt_identity()
    workSpace = Workspace.query.get_or_404(workspace_id)
    baselink = "http://localhost:5000"

    """
    check if the current user is the admin 
    """
    if workSpace.admin_id != currentUser:
        return jsonify({"error": "You don't have permission to invite members to this workspace"}), 403
    
    data = request.json
    email = data['email']

    if not email:
        return jsonify({"error": "Email is required"}), 400
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({"error": "Invalid email format"}), 400
 
    user = User.query.filter_by(email=email).first()

    if user:
        if ActiveSession(user.email):
            # inviteLink = f"{baselink}/dashboard?workspace_id={workspace_id}"
            inviteLink = url_for("dashboard", workspace_id=workspace_id, _external=True)
    print(inviteLink)
        # else:
        #     inviteLink = url_for("login",)



































































# def add_member(workspace_id):
    
#     currentUser = get_jwt_identity()
#     workspace = Workspace.query.get_or_404(workspace_id)
#     baselink = "http://localhost:5000"
#     emailtoken = generate_token(email)

#     """
#     check if the current user is the admin 

#     """
#     if workspace.admin_id != currentUser:
#         return jsonify({"error": "You don't have permission to invite members to this workspace"}), 403

#     Data = request.json
#     email = Data['email']
#     # role = Data.get('role', 'member')

    # if not email:
    #     return jsonify({"error": "Email is required"}), 400
    # if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
    #     return jsonify({"error": "Invalid email format"}), 400
    # # if role not in ['admin', 'member']:
    #     # return jsonify({"error": "Invalid role. Must be 'admin' or 'member'"}), 400
    
#     """
#     find the user in the database by email
#     """
    
#     user = User.query.filter_by(email=email).first()
#     """
#     is user is logged in create a link which directly redirects the user to the workspace which the user is invited to.
#     else, create a link first which redirects the user to signup.
#     """
#     if user:
#         if ActiveSession(user.email):
#             print(email)
#         else:
#             invitationLink = url_for('login',)
#             print("user is not logged in")
#     else:
#         print("no user")
#     # if not user:
#     #     try:
#     #         db.session.flush()
#     #     except IntegrityError:
#     #         db.session.rollback()
#     #         return jsonify({"error": "User with this email already exists"}), 400
    

    
#     existing_member = WorkspaceMember.query.filter_by(workspace_id=workspace_id, user_id=currentUser).first()
#     if existing_member:
#         return jsonify({"error": "User is already a member of this workspace"}), 400

#     # new_member = WorkspaceMember(workspace_id=workspace_id, user_id=currentUser, email=email, role=role)
#     # db.session.add(new_member)

#     # try:
#     #     db.session.commit()
#     # except IntegrityError:
#     #     db.session.rollback()
#     #     return jsonify({"error": "Failed to add member to workspace"}), 500

#     emailtoken = generate_token(email)
#     UserID = generate_token(currentUser)
#     # invitationlink = f"http://localhost:5000/invite?token={emailtoken}&UserId={UserID}"
#     newToken = InviteTokens(token=emailtoken,adminID = currentUser,email=email)
#     db.session.add(newToken)
#     try:
#         db.session.commit()
#     except IntegrityError:
#         db.session.rollback()
#         return jsonify({"error": "Failed to add token"}), 500

#     msg = Message(
#         subject="You're Invited!",
#         recipients=[email],
#         body=f"Hello, you've been invited! Click the link to join: {invitationlink}"
#     )

#     mail.send(msg)
#     return f"email sent successfully",200


