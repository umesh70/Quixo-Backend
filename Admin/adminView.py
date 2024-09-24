from flask_admin.contrib.sqla import ModelView
#from DataBase.db_config import User, Workspaces  

class UserView(ModelView):
    column_list = ('id', 'username', 'email','password','is_verified','otp')
    
class WorkspaceView(ModelView):
    column_list = ('workspace_id','workspace_name','description','admin_id','admin_mail')


class MemberView(ModelView):
    column_list = ('workspace_id','user_id','email','role','invited_at','joined_at')

class TokenView(ModelView):
    column_list = ('token','email')

class BoardView(ModelView):
    column_list = ('id', 'name', 'description', 'workspace_id')

class GradientView(ModelView):
    column_list = ('id', 'gradient')