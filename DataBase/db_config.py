from flask_sqlalchemy import SQLAlchemy
from Admin.adminView import UserView,workspaceView,MembersView,tokenview
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

    def __repr__(self):
        return f'<Workspace {self.workspace_name}>'

class WorkspaceMember(db.Model):
    __tablename__ = 'workspace_members'

    id = db.Column(db.Integer, primary_key=True)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.workspace_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    invited_at = db.Column(db.DateTime, default=datetime.utcnow)
    joined_at = db.Column(db.DateTime)

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

def init_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    admin = Admin(app, name='Admin panel', template_mode='bootstrap3')
    admin.add_view(UserView(User,db.session))
    admin.add_view(workspaceView(Workspace,db.session))
    admin.add_view(MembersView(WorkspaceMember,db.session))
    admin.add_view(tokenview(Token,db.session))
    with app.app_context():
        db.create_all()