import os
from flask_admin import Admin
from .models import Attendance, Deduction, Employee, PasswordResetToken, Payroll, db, User
from flask_admin.contrib.sqla import ModelView


def setup_admin(app):
    app.secret_key = os.environ.get('FLASK_APP_KEY', 'sample key')
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    admin = Admin(app, name='PayTrack Admin', template_mode='bootstrap4')

    # Add your models here, for example this is how we add a the User model to the admin
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Employee, db.session))
    admin.add_view(ModelView(PasswordResetToken, db.session))
    admin.add_view(ModelView(Attendance, db.session))
    admin.add_view(ModelView(Deduction, db.session))
    admin.add_view(ModelView(Payroll, db.session))

    # You can duplicate that line to add mew models
    # admin.add_view(ModelView(YourModelName, db.session))
