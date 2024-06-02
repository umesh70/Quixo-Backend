from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    otp = db.Column(db.Integer)

class Workspaces(db.Model):
    workspace_id = db.Column(db.Integer, primary_key=True)
    workspace_name = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    owner_id  =  db.Column(db.Integer, db.ForeignKey(User.id))
    owner = db.relationship('User', backref=db.backref('workspaces', lazy=True))

    def __repr__(self):
        return f'<Workspace {self.workspace_name}>'


def init_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()