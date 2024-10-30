import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Blueprint, request, jsonify
from DataBase.db_config import db, Board, Workspace, BoardGradients, Lists, Cards, Checklists, ChecklistItems
from flask_jwt_extended import jwt_required, get_jwt_identity

board_app = Blueprint('boards', __name__)
# /home/mansi/Quixo-Backend/vrenv/bin

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

@board_app.route('/get_board_details/<int:id>', methods = ['GET'])
@jwt_required()
def get_board_details(id):
    
    board = Board.query.filter_by(id = id).first()
    
    if not board:
        return jsonify({"error":f'Board with id {id} not found'}), 404
    
    return jsonify([{
        'id' : board.id,
        'name': board.name,
        'description' : board.description,
        'gradient' : board.gradient.gradient
    }])

@board_app.route('/edit_board_details/<int:board_id>', methods = ['PATCH'])
@jwt_required()
def edit_board_details(board_id):
    data = request.json
    name = data['name']
    description = data['description']

    board = Board.query.filter_by(id = board_id).first()
    print(board_id, name, description)

    if not board:
        return jsonify({'error' : 'Board not found'}), 404

    if not name:
        return jsonify({'error' : 'Name is required'}), 400
    
    board.name = name
    board.description = description

    db.session.commit()

    return jsonify({'message' : 'Board details updated successfully'}), 200


@board_app.route('/delete_board/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_board(id):

    board = Board.query.filter_by(id = id).first()
    
    if not board:
        return jsonify({"error":f'Board with id {id} not found'}), 404

    db.session.delete(board)
    db.session.commit()
    
    return jsonify({'success':f'Board deleted successfully'}),200

@board_app.route('/add_list/<int:id>', methods = ['POST'])
@jwt_required()
def add_list(id):

    data = request.json
    name = data['name']

    board = Board.query.filter_by(id = id).first()

    if not board:
        return jsonify({'error' : 'Board not found'}), 404
    
    if not name:
        return jsonify({'error' : 'Name is required'}), 400
    
    new_list = Lists(name = name, board_id = id, board = board)
    db.session.add(new_list)
    db.session.commit()

    return jsonify({'message' : 'List added successfully'}), 201

@board_app.route('/get_lists/<int:id>', methods = ['GET'])
@jwt_required()
def get_lists(id):

    board = Board.query.filter_by(id = id).first()

    if not board:
        return jsonify({'error' : 'Board not found'}), 404
    
    lists = board.lists
    list_data = [{'id':list.id, 'name':list.name} for list in lists]

    return jsonify(list_data), 200

@board_app.route('/add_card/<int:id>', methods = ['POST'])
@jwt_required()
def add_card(id):

    data = request.json
    title = data['title']

    list = Lists.query.filter_by(id = id).first()

    if not list:
        return jsonify({'error' : 'List not found'}), 404
    
    if not title:
        return jsonify({'error' : 'Title is required'}), 400
    
    new_card = Cards(title = title, list_id = id, list = list)
    db.session.add(new_card)
    db.session.commit()
    return jsonify({'message' : 'Card added successfully', 'card_id' : new_card.id, 'card_title' : new_card.title}), 201

@board_app.route('/get_cards/<int:id>', methods = ['GET'])
@jwt_required()
def get_cards(id):
    list = Lists.query.filter_by(id=id).first()

    if not list:
        return jsonify({'error': 'List not found'}), 404

    cards = list.cards or []

    card_data = []
    for card in cards:
        # Retrieve the checklist associated with this card
        checklist = card.checklist

        # Calculate total and completed checklist items
        total_checklist_items = len(checklist.items) if checklist else 0
        completed_items = sum(item.completed for item in checklist.items) if checklist else 0

        card_data.append({
            'id': card.id,
            'title': card.title,
            'description': card.description,
            'list_id': card.list_id,
            'total_checklist_items': total_checklist_items,
            'completed_items': completed_items
        })

    return jsonify(card_data), 200


@board_app.route('/change_gradient/<int:id>', methods = ['PATCH'])
@jwt_required()
def change_gradient(id):

    data = request.json
    gradient_value = data['gradient']

    board = Board.query.filter_by(id = id).first()

    if not board:
        return jsonify({'error' : 'Board not found'}), 404
    
    if not gradient_value:
        return jsonify({'error' : 'Gradient is required'}), 400
    
    gradient = BoardGradients.query.filter_by(gradient = gradient_value).first()

    if not gradient:
        return jsonify({'error' : 'Gradient not found'}), 404
    
    board.gradient = gradient
    db.session.commit()

    return jsonify({'message' : 'Gradient changed successfully'}), 200

    
@board_app.route('/delete_list/<int:id>', methods = ['DELETE'])
@jwt_required()
def delete_list(id):

    list = Lists.query.filter_by(id = id).first()

    if not list:
        return jsonify({'error' : 'List not found'}), 404
    
    db.session.delete(list)
    db.session.commit()

    return jsonify({'message' : 'List deleted successfully'}), 200
    
@board_app.route('/edit_card_title/<int:id>', methods = ['PATCH'])
@jwt_required()
def edit_card_title(id):

    data = request.json
    title = data['title']

    card = Cards.query.filter_by(id = id).first()

    if not card:
        return jsonify({'error' : 'Card not found'}), 404
    
    if not title:
        return jsonify({'error' : 'Title is required'}), 400
    
    card.title = title
    db.session.commit()

    return jsonify({'message' : 'Card title updated successfully'}), 200

@board_app.route('/edit_card_description/<int:id>', methods = ['POST'])
@jwt_required()
def edit_card_description(id):

    data = request.json
    description = data['description']

    card = Cards.query.filter_by(id = id).first()

    if not card:
        return jsonify({'error' : 'Card not found'}), 404
    
    card.description = description
    db.session.commit()

    return jsonify({'message' : 'Card description updated successfully'}), 200

@board_app.route('/delete_card/<int:id>', methods = ['DELETE'])
@jwt_required()
def delete_card(id):

    card = Cards.query.filter_by(id = id).first()

    if not card:
        return jsonify({'error' : 'Card not found'}), 404
    
    db.session.delete(card)
    db.session.commit()

    return jsonify({'message' : 'Card deleted successfully'}), 200

@board_app.route('/move_card/<int:id>', methods = ['PATCH'])
@jwt_required()
def move_card(id):

    card = Cards.query.filter_by(id = id).first()

    if not card:
        return jsonify({'error' : "Card not found"}), 404
    
    source_list_id = card.list_id

    data = request.json
    target_list_id = data['target_list_id']

    target_list = Lists.query.filter_by(id = target_list_id)

    if not target_list:
        return jsonify({'error' : "Target list not found"}), 404
    
    card.list_id = target_list_id
    db.session.commit()

    return jsonify({'message':"Card moved succesfully", "source_id":source_list_id, "target_id" : target_list_id}), 200
    
@board_app.route('/save_checklist/<int:id>', methods=['POST'])
@jwt_required()
def save_checklist(id):
    # Find the card by ID
    card = Cards.query.get(id)

    if not card:
        return jsonify({"error": "Card not found"}), 404

    # Get the checklist items from the request
    data = request.json
    checklist_items = data.get('checklist_items', [])

    # Check if the card already has a checklist
    checklist = Checklists.query.filter_by(card_id=id).first()

    if not checklist:
        # If no checklist exists for the card, create a new one
        checklist = Checklists(card_id=id)
        db.session.add(checklist)
        db.session.commit()

    # Get existing checklist items from the database
    existing_items = {item.id: item for item in checklist.items}

    # Prepare a set of item IDs received in the request
    incoming_item_ids = set()

    # Update or create checklist items
    for item_data in checklist_items:
        item_id = item_data.get('id')
        item_name = item_data.get('text', '').strip()  # Ensure we remove leading/trailing spaces
        item_completed = item_data.get('completed', False)

        if not item_name:
            # If the name is empty, skip creating a new item and delete existing ones
            if item_id and item_id in existing_items:
                db.session.delete(existing_items[item_id])
            continue

        if item_id and item_id in existing_items:
            # If the item exists, update it
            item = existing_items[item_id]
            item.name = item_name
            item.completed = item_completed
        else:
            # Only create new items if they have a non-empty name
            new_item = ChecklistItems(
                name=item_name,
                completed=item_completed,
                checklist_id=checklist.id
            )
            db.session.add(new_item)

        # Track the item IDs that are kept or updated
        if item_id:
            incoming_item_ids.add(item_id)

    # Remove items that are in the existing list but not in the incoming data
    for existing_item_id, existing_item in existing_items.items():
        if existing_item_id not in incoming_item_ids:
            db.session.delete(existing_item)

    # Commit the changes to the database
    db.session.commit()

    return jsonify({"message": "Checklist saved successfully"}), 200


@board_app.route('/get_checklist/<int:id>', methods=['GET'])
@jwt_required()
def get_checklist(id):
    # Find the card by ID
    card = Cards.query.get(id)

    if not card:
        return jsonify({"error": "Card not found"}), 404

    # Get the checklist for the card
    checklist = Checklists.query.filter_by(card_id=id).first()

    if not checklist:
        return jsonify({"error": "Checklist not found"}), 404

    # Retrieve the checklist items
    checklist_items = [{
        "id": item.id,
        "text": item.name,
        "completed": item.completed
    } for item in checklist.items]

    return jsonify({
        "checklist_id": checklist.id,
        "card_id": card.id,
        "checklist_items": checklist_items
    }), 200



