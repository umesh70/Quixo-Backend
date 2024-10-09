import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import request, jsonify, Blueprint, url_for,redirect
from DataBase.db_config import db, User, Workspace, WorkspaceMember,WorkspaceToken
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_jwt_extended import jwt_required
from flask import request, jsonify
import re
from Utilities.utilities import generate_token, mail, active_session
from flask_mail import Message
import random


Workspace_app = Blueprint('workspace_points', __name__)

@Workspace_app.route('/create_workspace', methods=['POST'])
@jwt_required()
def create_workspace():

    data=request.json
    admin_mail = data['email']
    workspace_name = data['name']
    description = data['description']

    admin_id = get_jwt_identity()
    user = User.query.filter_by(id=admin_id).first()
    
    print(User.query.all()[0].id, admin_id)
    
    if (user.id != admin_id) and (user.email != admin_mail):
        return jsonify({'error':'Please enter correct email'}),422
    
    if not user:
        return jsonify({'error': 'Invalid user'}), 404
    
    new_workspace = Workspace(workspace_name=workspace_name,
                               admin_mail=admin_mail, admin_id=admin_id, description=description)

    db.session.add(new_workspace)
    db.session.commit()

    workmember = WorkspaceMember(
                workspace_id = new_workspace.workspace_id,     
                user_id = user.id,
                email = user.email,
                status= "Admin"
            )
    
    db.session.add(workmember)
    db.session.commit()
    return jsonify({'message': f'Workspace {workspace_name} created successfully'}), 201


@Workspace_app.route('/get_user_workspaces', methods=['GET'])
@jwt_required()
def get_user_workspaces():
    user_id = get_jwt_identity()
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

@Workspace_app.route('/delete_workspace/<id>', methods=['DELETE'])
@jwt_required()
def delete_workspace(id):

    workspace = Workspace.query.filter_by(workspace_id=id).first()

    if not workspace:
        return jsonify({'error': 'Workspace does not exist'}), 404

    db.session.delete(workspace)
    db.session.commit()
    return jsonify({'message': 'Workspace deleted successfully'}), 200


@Workspace_app.route('/edit_workspace_details/<id>', methods = ['PATCH'])
@jwt_required()
def edit_workspace_details(id):

    data = request.json
    name = data['name']
    description = data['description']

    workspace = Workspace.query.filter_by(workspace_id = id).first()

    if not workspace:
        return jsonify({'error' : 'Workspace does not exist'}), 404

    if not name:
        return jsonify({'error': 'Name is required'}), 400
    
    workspace.workspace_name = name
    workspace.description = description
    db.session.commit()

    return jsonify({'message': 'Details updated successfully'}), 200


"""
Endpoint for sending an invite via email(Send invite link to their email)
"""

@Workspace_app.route('/add_member/<workspace_id>',methods = ['POST'])
@jwt_required()
def add_member(workspace_id):

    base_url = os.getenv('invitation_base_url')
    current_user_id = get_jwt_identity()

    workspace = Workspace.query.get_or_404(workspace_id)   
    workspace_name = workspace.workspace_name

    # Check if the current user is the admin
    if workspace.admin_id != current_user_id:
        return jsonify({"error": "Only admins have permission to invite members to a workspace"}), 403
    
    data = request.json
    email = data.get('email')

    if not email:
        return jsonify({"error": "Email is required"}), 400
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({"error": "Invalid email format"}), 400
 
    user = User.query.filter_by(email = email).first()

    # Check if the user is already a member of the workspace
    existing_member = WorkspaceMember.query.filter_by(workspace_id=workspace_id, email=email).first()
    if existing_member:
        return jsonify({"error": "User is already a member of this workspace"}), 400

    #Check whether a link to the asked workspace, email was sent earlier too
    if WorkspaceToken.query.filter_by(email = email, workspace_id = workspace_id).first():
        return jsonify({"error": f"Invitation link was already sent for {workspace_name} workspace to {email} email"}), 400
    
    # Generate a unique invitation token
    invitation_token = generate_token(email + workspace_id)

    if user:
        if active_session(user.email):
            workmember = WorkspaceMember(
                workspace_id = workspace_id,
                user_id = user.id,
                email = user.email,
                status= "Member"
            )
            db.session.add(workmember)
            db.session.commit()
            invite_link = f"{base_url}/dashboard/{workspace_id}/{workspace_name.replace(' ', '')}/boards"

        else:
            invite_link = f"{base_url}/login?token={invitation_token}&email={email}&workspace_id={workspace_id}"
            inivite_info = WorkspaceToken(
                token = invitation_token,
                email = email,
                workspace_id = workspace_id
            )
            db.session.add(inivite_info)
        
    else:
            invite_link = f"{base_url}/signup?token={invitation_token}&email={email}&workspace_id={workspace_id}"
            inivite_info = WorkspaceToken(
                token=invitation_token,
                email= email,
                workspace_id = workspace_id
            )
            db.session.add(inivite_info)
    print(invite_link)

    try:
        db.session.commit()
        msg = Message()
        msg = Message(f'Invitation to join {workspace_name} workspace on Quixo',
        recipients=[email])
        msg.body = f"Hi,\n\nYou have been invited to join the workspace '{workspace_name}' on Quixo.\n\nPlease use the following link to join:\n\n{invite_link}\n\nBest regards"
        mail.send(msg)
        
        return jsonify({
            "message": "Invitation sent successfully",
            "invite_link": invite_link
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@Workspace_app.route('/get_members/<workspace_id>', methods = ['GET'])
@jwt_required()
def get_members(workspace_id):
    try:
        if not workspace_id:
            return jsonify({'error': 'workspace_id is required'}), 400
        
        workspace = Workspace.query.get_or_404(workspace_id)

        workspace_members = workspace.members
        members_list = []

        for member in workspace_members:
            data = {
                "id" : member.id,
                "user_id" : member.user_id,
                "name" : member.user.username,
                "user_color" : member.user.user_color,
                "email" : member.email,
                "status" : member.status,
            }
            members_list.append(data)

        return jsonify({"members_lists":members_list, "admin_id" : workspace.admin_id}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500



"""
CASES

1. the user who wants to leave the workspade is a normal user
2. the admin wants to leave the workspace
    2.1 check if there are any other admin
        2.1.1 if yes remove the admin 
        2.1.2 if not check if there are other members in the workspace except the admin who is trying to leave 
        2.1.3 if not delete the workspace 
        2.1.4 if yes, assign anyother person randomly the admin
"""


@Workspace_app.route('/leave_workspace/<workspace_id>', methods=['POST'])
@jwt_required()
def leave_workspace(workspace_id):
    data = request.json
    new_admin_id = data['new_admin_id']

    curr_user_id = get_jwt_identity()

    # Check whether the workspace exists or not

    workspace = Workspace.query.filter(Workspace.workspace_id == workspace_id).first()
    
    if not workspace:
        return jsonify({'error' : 'Workspace does not exists'}), 400

    # Check if the current user is a member of the workspace

    leaving_member = WorkspaceMember.query.filter(
        WorkspaceMember.user_id == curr_user_id,
        WorkspaceMember.workspace_id == workspace_id
    ).first()

    if not leaving_member:
        return jsonify({'error': 'You are not a member of this workspace'}), 404

    if leaving_member.status == 'Admin':

        total_members = len(list(workspace.members))

        if total_members == 1:
            # Case 2.1.3: No other members, delete the workspace
            db.session.delete(leaving_member)
            db.session.delete(workspace)
            db.session.commit()
            return jsonify({'message' : 'You have left the workspace and the workspace was deleted successfully'}), 200
        
        # Case 2.1.4: Assign another person as admin
        if not new_admin_id:
            return jsonify({"error" : "Please send the id of new admin"}), 400
        
        new_admin = WorkspaceMember.query.filter(WorkspaceMember.workspace_id == workspace_id, WorkspaceMember.user_id == new_admin_id).first()

        if new_admin_id == curr_user_id:
            return jsonify({"error" : "In order to leave the workspace make some other member as admin"}), 406
        
        if not new_admin:
            return jsonify({"error" : f"User with id {new_admin_id} is not a member of workspace {workspace.workspace_name}"}), 404
        
        
        new_admin.status = 'Admin'
        new_admin.workspace.admin_id = new_admin_id
        new_admin.workspace.admin_mail = new_admin.email
        db.session.delete(leaving_member)
        db.session.commit()

        return jsonify({'message': f'You have left the workspace and member {new_admin.user.username} is now new admin'}), 200

    else:
        # Case 1: Normal user wants to leave the workspace
        try:
            db.session.delete(leaving_member)
            db.session.commit()

            return jsonify({'message': 'You have left the workspace successfully'}), 200
        
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': 'An error occurred while leaving the workspace', 'error': str(e)}), 500




@Workspace_app.route('remove_member/<workspace_id>',methods=['POST'])
@jwt_required()
def remove_member(workspace_id):
    data = request.json
    user_id = data['user_id']
    curr_user_id = get_jwt_identity()

    # check if the workspace exists or not

    workspace = Workspace.query.filter(Workspace.workspace_id == workspace_id).first()
    if not workspace:
        return jsonify({'error' : 'Workspace does not exists'}), 400    
     
    # check if the current user is the admin

    is_admin = workspace.admin_id == curr_user_id
   
    if not is_admin:
        return jsonify({'error' : 'Workspace members can only be removed by admin'}), 403
        
    to_remove = WorkspaceMember.query.filter(WorkspaceMember.user_id == user_id, WorkspaceMember.workspace_id == workspace_id).first()

    if not to_remove:
        return jsonify({'error' : f'No user with user id {user_id} exists for workspace {workspace.workspace_name}'}), 400
       
    if user_id == workspace.admin_id:
            return jsonify({'error':'Admins cannot remove themselves'}), 405 

    db.session.delete(to_remove)
    db.session.commit()

    return jsonify({'message':'Member removed successfully'}),200


    