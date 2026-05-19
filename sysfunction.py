
from Apex_clinic_app.extensions import db
from Apex_clinic_app.model_mapping import syscarrier
from datetime import datetime,timezone



def backendsysuser():
    admin = syscarrier(
                    sys_name =input("Name:"),
                    email=input("Email:"),
                    is_sys=True,
                    last_active=datetime.now(timezone.utc))
    admin.set_password(input("Password:"))               
    db.session.add(admin)
    db.session.commit()
   