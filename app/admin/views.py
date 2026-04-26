from flask import redirect, url_for
from flask_admin import expose, AdminIndexView
from flask_jwt_extended import verify_jwt_in_request, get_jwt

class AdminView(AdminIndexView):
    def is_accessible(self):
        try:
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims["roles"]
            return user_role == "admin"
        except Exception:
            return False

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('frontend.index', error='forbidden'))

    @expose('/')
    def index(self):
        return self.render('layout/admin.html')

    @expose('/settings')
    def settings(self):
        return self.render('page/settings.html')