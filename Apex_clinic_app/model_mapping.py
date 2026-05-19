import  uuid
from Apex_clinic_app import db 
from sqlalchemy import CheckConstraint, Column,String,Integer,Boolean,DateTime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime,timezone




class patient(db.Model):
    __tablename__ = 'Diagnosis_table'
    patient_id = Column(String(25),primary_key=True)
    Disease = Column(String(100),nullable=False)
    Fever = Column(String,nullable=False)
    Cough = Column(String,nullable=False)
    Fatigue	= Column(String,nullable=False)
    Difficult_breath = Column(String,nullable=False)
    Age = Column(Integer,nullable=False)
    Gender = Column(String(15),nullable=False)
    Blood_Pressure = Column(String(25),nullable=False)
    Cholesterol_Level = Column(String(25),nullable=False)
    Outcome_Variable = Column(String(25),nullable=False)
    __table_args__ = (
        CheckConstraint("Blood_pressure in ('High','Low','Normal')",name="Bloodcheck_input"),
        CheckConstraint("Cholesterol_Level in ('High','Low','Normal')",name="cholesterolcheck_input"),
        CheckConstraint("Outcome_Variable in ('Positive','Negative')",name="outcomecheck_inpcommand"))



class users(db.Model,UserMixin):
    __bind_key__ = "db_2"
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    username =Column(String(35),nullable=False)
    firstname = Column(String(100), nullable=False)
    lastname = Column(String(100),nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    user_password = Column(String(2000), nullable=False)
    email_verified = Column(Boolean,default=False)
    update_click = Column(Boolean,default=False)
    approval = Column(Boolean,default = False)
    deny = Column(Boolean,default=False)
    is_admin = Column(Boolean,default=False)
    last_active = Column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc))
    user_update_per_patient =Column(String(35),default="pid",nullable=False)
    user_patient_denied = Column(String(35),default="patient",nullable=False)
    user_id_denied_per_patient = Column(Integer,default=0, nullable=False)
    user_blocked  = Column(Boolean,default= False)
    useraction_count = db.Column(db.Integer, default = 0)
    systab = db.relationship("systab",back_populates="users",lazy="joined",cascade="all,delete")
    unlock = db.relationship("unlock",back_populates="users",lazy="joined",cascade="all,delete")
    @property
    def is_sys(self):
        return False
    
    def get_id(self):
        return f"user:{self.user_id}"
    
    def set_password(self, password):
        self.user_password = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.user_password,password)


class systab(db.Model):
    __bind_key__ = "db_2"
    __tablename__ = "systab"
    sys_id = db.Column(db.Integer,primary_key =True)
    lock_admin_approval = db.Column(db.Boolean,default = False)
    lock_admin_rejection = db.Column(db.Boolean,default = False)
    number_of_admin_approvals = db.Column(db.Integer, default = 0)
    number_of_admin_rejections = db.Column(db.Integer, default = 0)
    narration =  db.Column(db.String(5000), nullable = False)
    user_sys_id = db.Column(db.Integer,db.ForeignKey("users.user_id"),nullable=False)
    users = db.relationship("users",back_populates="systab")
    

class admin_token(db.Model):
    __bind_key__ = "db_2"
    __tablename__ = "admin_token"
    token_id = db.Column(db.Integer,primary_key = True)
    expired_token = db.Column(db.Integer, default = 0)
    token = db.Column(db.String, nullable = False)


class syscarrier(db.Model,UserMixin):
    __bind_key__ = "db_2"
    __tablename__ = "syscarrier"
    sys_id = db.Column(db.Integer,primary_key = True)
    sys_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String,nullable=False)
    sys_password = db.Column(db.String, nullable=False)
    is_sys = db.Column(db.Integer,default=0)
    last_active = Column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc))
    @property
    def is_admin(self):
        return False
    def get_id(self):
        return f"sys:{self.sys_id}"
    def set_password(self, password):
        self.sys_password = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.sys_password,password)
    


class unlock(db.Model):
    __bind_key__ = "db_2"
    __tablename__ = "unlock"
    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    idx = db.Column(db.Integer, default = 0)
    pid = db.Column(db.String(20), default="pid")
    users = db.relationship("users",back_populates="unlock")
    
   

    









