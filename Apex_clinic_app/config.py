
import secrets,os,socket
from datetime import timedelta
from Apex_clinic_app.app_functions import read_secret



hostname        = os.getenv("DB_HOST")
orapassword     = read_secret("/Apex_clinic_app/secrets/ora_password.txt")
oraserver       = read_secret("/Apex_clinic_app/secrets/ora_server.txt")
orauser         = read_secret("/Apex_clinic_app/secrets/ora_user.txt")
ora_port        = os.getenv("ora_port")
msqldriver      = os.getenv("driver_mssql")
msqlpassword    = read_secret("/Apex_clinic_app/secrets/mssql_password.txt")
msqluser        = read_secret("/Apex_clinic_app/secrets/mssql_user.txt")
msql_port       = os.getenv("msql_port")
redis_p         = os.getenv("redis_pass")
msqldatabase    = read_secret("/Apex_clinic_app/secrets/database_mssql.txt")
key             = read_secret("/Apex_clinic_app/App_key/a_key.txt")


class Config(object):

    SECRET_KEY = key

    SQLALCHEMY_DATABASE_URI = f'mssql+pyodbc://{msqluser}:{msqlpassword}@{hostname}:{msql_port}/{msqldatabase}?driver={msqldriver}'
    SQLALCHEMY_BINDS = {'db_2':f'oracle+oracledb://{orauser}:{orapassword}@{hostname}:{ora_port}/?service_name={oraserver}'}
    SQLALCHEMY_ENGINE_OPTIONS= {"pool_pre_ping": True,"pool_recycle": 3600}

    REDIS_URL_QUEUE = f"redis://:{redis_p}@redis:6379/0"
    REDIS_URL_STORE = f"redis://:{redis_p}@redis:6379/1"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_DOMAIN = None
    SESSION_COOKIE_SAMESITE ="Lax"
    SESSION_COOKIE_SECURE = False
    SESSION_TYPE ="filesystem"
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=10)
    INACTIVE_SESSION_TIME = 180
    RESIGNIN_GRACEPERIOD= 180
    APPROVAL_EXPIRED = 120
    
    
    MAIL_SERVER = "mailhog"
    MAIL_PORT =     1025
    MAIL_USE_TLS =  False
    MAIL_USE_SSL = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    MAIL_DEFAULT_SENDER = 'noreply@apexclinic.com'




