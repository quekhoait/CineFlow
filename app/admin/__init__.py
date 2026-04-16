from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from app import db
from app.models import Rules, Film

admin = Admin(name='CineFlow Admin')
admin.template_mode = 'bootstrap4'

admin.add_view(ModelView(Film, db.session))
admin.add_view(ModelView(Rules, db.session))