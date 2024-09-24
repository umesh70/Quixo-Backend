from flask_sqlalchemy import SQLAlchemy
from Admin.adminView import UserView, WorkspaceView, MemberView, TokenView, BoardView, GradientView
from flask_admin import Admin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    otp = db.Column(db.Integer)

    # Relationship to the workspaces the user administers
    workspaces_administered = db.relationship('Workspace', back_populates='admin', cascade="all, delete-orphan")

    # Relationship to workspace memberships
    workspace_memberships = db.relationship('WorkspaceMember', back_populates='user', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<User {self.username}>'


class Workspace(db.Model):
    __tablename__ = "workspaces"
    
    workspace_id = db.Column(db.Integer, primary_key=True)
    workspace_name = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    admin_id  =  db.Column(db.Integer, db.ForeignKey(User.id))
    admin_mail = db.Column(db.String(50), nullable=False)

    # Relationship to the user who is the admin of this workspace
    admin = db.relationship('User', back_populates='workspaces_administered')

    # Relationship to the members of this workspace
    members = db.relationship('WorkspaceMember', back_populates='workspace', cascade="all, delete-orphan")

    # Relationship to the boards which belong to this workspace
    board = db.relationship('Board', back_populates = 'workspace', cascade = "all, delete-orphan")

    def __repr__(self):
        return f'<Workspace {self.workspace_name}>'

class WorkspaceMember(db.Model):
    __tablename__ = 'workspace_members'

    id = db.Column(db.Integer, primary_key=True)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.workspace_id'), nullable=False)
    workspacName = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(255), nullable=False)

    # Relationship to the workspace this membership belongs to
    workspace = db.relationship('Workspace', back_populates='members')

    # Relationship to the user who is a member of this workspace
    user = db.relationship('User', back_populates='workspace_memberships')

    __table_args__ = (
        db.UniqueConstraint('workspace_id', 'email', name='uq_workspace_member_email'),
    )

    def __repr__(self):
        return f'<WorkspaceMember {self.email} in {self.workspace.workspace_name}>'

class Token(db.Model):
    __tablename__ = "tokens"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    token = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<Token {self.token}>'


class WorkspaceToken(db.Model):
    __tablename__ = "workspacetokens"
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(255), nullable=False)
    
    def __repr__(self):
        return f'<Token {self.token}>'

class Board(db.Model):
    __tablename__ = "boards"

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable = False)
    description = db.Column(db.String(250))
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.workspace_id'), nullable = False)
    gradient_id = db.Column(db.Integer, db.ForeignKey('board_gradients.id'), nullable = False)

    #Relationship to the workspace to which this board belongs
    workspace = db.relationship('Workspace', back_populates = 'board')

    #Relationship to the gradient which this board uses
    gradient = db.relationship('BoardGradients', back_populates = 'boards')


    def __repr__(self):
        return f'<Board {self.name}>'
    
class BoardGradients(db.Model):
    __tablename__ = "board_gradients"

    id = db.Column(db.Integer, primary_key = True)
    gradient = db.Column(db.String(100), nullable = False)

    #Relationship to the boards which use this gradient
    boards = db.relationship('Board', back_populates = 'gradient', cascade = "all, delete-orphan")

    def __repr__(self):
        return f'<Gradient {self.id}>'


def init_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    admin = Admin(app, name='Admin panel', template_mode='bootstrap3')
    admin.add_view(UserView(User,db.session))
    admin.add_view(WorkspaceView(Workspace,db.session))
    admin.add_view(MemberView(WorkspaceMember,db.session))
    admin.add_view(TokenView(Token, db.session))
    admin.add_view(BoardView(Board, db.session))
    admin.add_view(GradientView(BoardGradients, db.session))

    with app.app_context():
        db.create_all()