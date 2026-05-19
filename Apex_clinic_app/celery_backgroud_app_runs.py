from Apex_clinic_app.extensions import db,logging
from .model_mapping import users,admin_token,unlock
from celery import shared_task
import pandas as pd,os
from flask import session
from datetime import datetime,timezone, timedelta
from sqlalchemy import or_





@shared_task 
def expires_action(user_id,patient_id): 
    user = users.query.get(user_id)
    if user.user_update_per_patient != patient_id:
        logging.info("Patient record for current user not found")
    if user.approval:
        user.email_verified = False
        user.update_click = False
        user.user_update_per_patient = None 
        user.approval = False
        db.session.commit()

@shared_task 
def expires_action_deny(user_id,patient_id):
    try: 
        user = users.query.get(user_id)
        if not user:
            logging.error("Expire action deny task:User not found")
        if user.deny:
            user.deny = False
            for record in user.unlock:
                if record.pid == patient_id:
                    record.pid = f"{patient_id}:Denied => Unlocked"
        unlock_records = user.unlock
        for record in unlock_records:
                if record.pid == patient_id:
                    record.pid = f"{patient_id}:Denied => Unlocked"
        user.user_update_per_patient = None
        db.session.commit()
    except Exception:
         logging.exception("Error unlocking denied parent record modification")


@shared_task
def delete_admintoken(token):
    try:
        deleted_count = admin_token.query.filter(or_(admin_token.token == token,admin_token.expired_token == True
                        )).delete(synchronize_session=False)
        db.session.commit()
        logging.info(f"{deleted_count} used admin token deleted successfully")

    except Exception:
        db.session.rollback()
        logging.exception("Error deleting admin token after use")
             

        
@shared_task
def automate_upload(filename,previous_rows):
    conn = db.engine.raw_connection()
    path = os.path.abspath('/Apex_clinic_app/clinic_record')
    fullpath        = os.path.join(path,filename)
    if filename.startswith("Cancer"):
        df = pd.read_excel(fullpath)
    else:
        df = pd.read_csv(fullpath)
    current_rows    = df.shape[0]
    if current_rows >  previous_rows:
                        new_rows = df.iloc[previous_rows:]
                        rows = [tuple(x) for x in new_rows.itertuples(index = False, name = None)]
                        cursor = conn.cursor()
                        cursor.fast_executemany = True
                        try:
                            if filename == "Cancer_Patient_Data.xlsx":
                                cursor.execute("{CALL bulk_load_medical_facts (?)}", (rows,))
                            cursor.execute("{CALL upsert_diagnosis (?)}", (rows,))
                            conn.commit()     
                            return f"{len(new_rows)} new rows have been updated successfully"
                        except Exception as e:
                            conn.rollback()
                            logging.error(f"Error\n{e}")
                        finally:
                            cursor.close()
                            conn.close()
    return "No new rows detected"
        
    


@shared_task(name="incremental_upload")
def file_count(filename):
    
    path = os.path.abspath('/Apex_clinic_app/clinic_record')
    fullpath        = os.path.join(path,filename)
    if filename.startswith("Cancer"):
        df = pd.read_excel(fullpath) 
    else:
        df = pd.read_csv(fullpath) 
    current_rows    = df.shape[0]
    automate_upload.apply_async(args =[filename,current_rows],eta=datetime.now(timezone.utc) + timedelta(minutes=1))
    


@shared_task
def unlock_admin_review(admin_user_id):
    user = users.query.get(admin_user_id)
    try:
        if user:
            for REC in user.systab:
                if not REC:
                     logging.info("Sytem table for user did not return any rows")
                REC.number_of_admin_approvals = 0
                REC.lock_admin_approval = False
                REC.number_of_admin_rejections = 0
                REC.lock_admin_rejection = False
            db.session.commit()
    except Exception:
        logging.exception("Error unlocking Admin user review operation")
        