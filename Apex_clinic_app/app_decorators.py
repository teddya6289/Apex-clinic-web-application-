
from functools import wraps
from flask import flash, request,session,redirect, url_for, render_template
from flask_login import current_user
from Apex_clinic_app.model_mapping import patient,users
from Apex_clinic_app.extensions import db

def email_verification_approval(f):
    @wraps(f)
    def check_email_verification(*args, **kwargs):

        if not current_user.is_authenticated:
            flash("Invalid request: User unauthenticated!", "danger")
            return redirect(url_for("auth.login"))
        
        user = users.query.filter_by(user_id = current_user.user_id).first()
        if not user:
            flash("User record not found.","danger")
            return redirect(url_for("auth.login"))
        
        endpoint_actions = {
                            "user.deleterecord": "delete",
                            "user.updatepatient": "update",
                            "user.addpatient": "add"}

        action = endpoint_actions.get(request.endpoint,"process")

        patient_id = kwargs.get("patientID")
        session['clickedroute'] = request.path
        
        if not patient_id:
            return "Broken patient record"
        
        denied_patients = []
        for unlockfeatures in user.unlock:
            if unlockfeatures.id_user == current_user.user_id and unlockfeatures.pid:
                denied_patients.extend(unlockfeatures.pid.split(','))
        
        if str(patient_id) in denied_patients:
                if request.endpoint == "user.addpatient":
                    flash(f"Current user have been denied permission to {action} the patient record.Please try again denial expires","info")
                    return redirect(url_for("user.userhomepage"))
                
                flash(f"Current user have been denied permission to {action} the patient record.Please try again after denial expires","info")
                return redirect(url_for("user.records"))
        
        if not current_user.email_verified and not current_user.update_click:
            return redirect(url_for("ev.sendemail", pid=patient_id))
        
        if current_user.user_update_per_patient != patient_id:
            if request.endpoint == "user.addpatient":
                flash(f"Current user {action} request is still running.Please try again after admin action","danger")
                return redirect(url_for("user.userhomepage"))
       
            flash(f"Current user {action} request is still running.Please try again after admin action","danger")
            return redirect(url_for("user.records"))
       
      
        
        
        if current_user.deny and current_user.user_id == user.user_id_denied_per_patient and current_user.user_patient_denied == patient_id:
                flash(f"Request to {action} {patient_id} denied.", "info")
                return redirect(url_for("user.records"))
        
        if not current_user.approval:
            if request.endpoint == "user.addpatient":
                flash(f"Email verified but request pending admin action. You cannot {action} this record yet.", "danger")
                return redirect(url_for("user.userhomepage"))
            
            flash(f"Email verified but request pending admin action. You cannot {action} this record yet.", "danger")
            return redirect(url_for("user.records"))
        
        flash(f"Request approved for 2 minutes. Proceed to {action} record.", "success")
        return f(*args, **kwargs)
    return check_email_verification





