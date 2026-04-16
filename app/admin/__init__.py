from flask_admin import Admin
from flask_admin.theme import Bootstrap4Theme
from app.admin.views import AdminView

custom_theme = Bootstrap4Theme()
custom_theme.base_template = 'layout/admin.html'

admin = Admin(name='Cineflow Admin', theme=custom_theme, index_view=AdminView(name='Dashboard', endpoint='admin'))