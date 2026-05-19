from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager
from flask_session import Session





db = SQLAlchemy()
mail = Mail()
login_manager = LoginManager()
app_session =Session()



def logingprocess():
    import logging
    logging.basicConfig(    filename  ="app_logs",
                            level     =logging.DEBUG,
                            format    ="%(asctime)s - %(levelname)s - %(message)s")
    return logging

logging = logingprocess()