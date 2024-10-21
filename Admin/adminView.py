from flask_admin.contrib.sqla import ModelView
#from DataBase.db_config import User, Workspaces  

class UserView(ModelView):
    column_list = ('id', 'username', 'email','password','is_verified','otp','user_color')
    
class WorkspaceView(ModelView):
    column_list = ('workspace_id','workspace_name','description','admin_id','admin_mail')


class MemberView(ModelView):
    column_list = ('workspace_id','user_id','email','status')

class TokenView(ModelView):
    column_list = ('token','email')

class BoardView(ModelView):
    column_list = ('id', 'name', 'description', 'workspace_id')

class GradientView(ModelView):
    column_list = ('id', 'gradient')

class WorkspaceTokenView(ModelView):
    column_list = ('token','email')

class ListView(ModelView):
    column_list = ('id', 'name', 'board_id')

class CardView(ModelView):
    column_list = ('id', 'title', 'description', 'list_id')

class ChecklistView(ModelView):
    column_list = ('id', 'card_id')

class ChecklistItemsView(ModelView):
    column_list = ('id', 'name', 'completed', 'checklist_id')