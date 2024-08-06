from flask_admin.contrib.sqla import ModelView
#from DataBase.db_config import User, Workspaces  

class UserView(ModelView):
    column_list = ('id', 'username', 'email','password','email','is_verified','otp')
    
class workspaceView(ModelView):
    column_list = ('workspace_id','workspace_name','description','admin_id','admin_mail')
