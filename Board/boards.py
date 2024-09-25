import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Blueprint, request, jsonify
from DataBase.db_config import db, Board, Workspace, BoardGradients
from flask_jwt_extended import jwt_required

board_app = Blueprint('boards', __name__)

@board_app.route('/create_board', methods = ['POST'])
@jwt_required()
def create_board():

    data = request.json
    name = data['name']
    description = data['description']
    gradient_value = data['gradient']
    workspace_id = data['workspace_id']

    workspace = Workspace.query.filter_by(workspace_id = workspace_id).first()

    if not workspace_id or not name or not gradient_value:
        return jsonify({'error': 'name, workspace_id and gradient are required'}), 400
    
    if not workspace:
        return jsonify({'error': 'workspace not found'}), 404
    
    gradient = BoardGradients.query.filter_by(gradient=gradient_value).first()

    if not gradient:
        return jsonify({'error': 'Gradient not found'}), 404
    
    new_board = Board(name = name, description = description, gradient = gradient, workspace_id = workspace_id, workspace = workspace)
    db.session.add(new_board)
    db.session.commit()
    return jsonify({'message': f'Board {name} created successfully'}), 201

@board_app.route('/get_boards/<int:workspace_id>', methods = ['GET'])
@jwt_required()
def get_boards(workspace_id):

    boards = Board.query.filter_by(workspace_id = workspace_id).all()
    board_list = []
    for board in boards:
        board_data = {
            'id' : board.id, 
            'name' : board.name,
            'description' : board.description,
            'gradient' : board.gradient.gradient if board.gradient else None,
            'workspace_id' : board.workspace_id
        }
        board_list.append(board_data)

    return jsonify(board_list), 200

@board_app.route('/get_board_gradients', methods = ['GET'])
@jwt_required()
def get_board_gradients():
    gradients = BoardGradients.query.all()
    gradient_list = []
    for gradient in gradients:
        gradient_data = {
            'id' : gradient.id,
            'gradient' : gradient.gradient
        }
        gradient_list.append(gradient_data)
    
    return jsonify(gradient_list), 200