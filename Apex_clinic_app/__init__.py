from flask import Flask
from Apex_clinic_app.config import Config
from Apex_clinic_app.extensions import db,login_manager,mail,app_session



def creatapp():

    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    app_session.init_app(app)
    
    from Apex_clinic_app.regular_user_route import regular_user_bp
    from Apex_clinic_app.user_logins_route import users_bp
    from Apex_clinic_app.send_verify_email import send_verify_email_bp
    from Apex_clinic_app.model_mapping import users,syscarrier
    from Apex_clinic_app.homepage import main_bp
    from Apex_clinic_app.admin_user_route import admin_bp
    from Apex_clinic_app.cli import register_cli
    from Apex_clinic_app.app_utils import logout_inactive_user
    from Apex_clinic_app.system_route import sys_bp
    from AI_assist import Aiassist_bp
    from Apex_clinic_app.celeryconfig import init_celery

    init_celery(app)
   
    app.register_blueprint(regular_user_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(send_verify_email_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(sys_bp)
    app.register_blueprint(Aiassist_bp)
    register_cli(app)
    
    @login_manager.user_loader
    def load_user(user_key):
        try:

            user_type, user_id = user_key.split(":")

            if user_type == "user":
                    return users.query.get(int(user_id))

            if user_type == "sys":
                return syscarrier.query.get(int(user_id))

        except Exception:
            return None

        return None
    
    login_manager.login_view    = "main.mainpage"
    login_manager.login_message = "Login Required"

    logout_inactive_user(app)

    print(app.url_map)
    return app

   










