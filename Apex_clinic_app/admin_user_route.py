from Apex_clinic_app.extensions import db,logging
from Apex_clinic_app.model_mapping import users,systab,generate_password_hash,unlock
from flask import Blueprint, render_template,redirect, url_for, flash,session,request
from Apex_clinic_app.app_utils import admin_route_secured
from flask_login import login_required,current_user
from datetime import datetime, timezone,timedelta
from Apex_clinic_app.celery_backgroud_app_runs import expires_action_deny, unlock_admin_review,expires_action
from Apex_clinic_app.app_forms import adminform





admin_bp = Blueprint('admin', __name__)

admin_route_secured(admin_bp)

@admin_bp.route('/homeadmin')
def homeadmin():
    return render_template('admin_homepage.html')


@admin_bp.route("/pending_users",methods = ["GET","POST"])
@login_required
def pending_users():
    try:
        Users = users.query.filter_by(approval=False,email_verified=True,is_admin = False).all()
        users_count = len(Users)
        return render_template("pending_users.html", user=Users,users_count = users_count)
    except Exception:
         logging.exception("Error")


@admin_bp.route("/approve/<int:user_id>/<string:patient_id>",methods = ["GET","POST"])
@login_required
def approve_user(user_id,patient_id):

        user = users.query.get(user_id)
        admin_user = users.query.filter_by(user_id=current_user.user_id).first()
        for sysfeatures in admin_user.systab:
            if not sysfeatures:
                logging.info(" No Sysfeatures instance")
                flash("System error occurred", "danger")
                return redirect(url_for("admin.homeadmin"))
            if sysfeatures.lock_admin_approval == 1:
             flash(f"Approval privilleges exceeded:{current_user.firstname} locked for 24 hours")
             return redirect(url_for("admin.homeadmin"))
        if not user:
                flash("User not found", "danger")
                return redirect(url_for("admin.homeadmin"))
        try:
            if user.user_update_per_patient == patient_id:
                user.approval = True
                user.useraction_count += 1
                sysfeatures.number_of_admin_approvals += 1
                newsysreca = systab(narration = (f"Date:{datetime.now(timezone.utc)}| Admin user:{current_user.firstname} granted approval to "
                                         f"{user.firstname} to perform a sensitive task as part of an ongoing job operation"),
                                    number_of_admin_approvals = sysfeatures.number_of_admin_approvals,
                                    user_sys_id = current_user.user_id) 
                

                if sysfeatures.number_of_admin_approvals == 10:
                    sysfeatures.lock_admin_approval = True
                    flash("Approval privileges exceeded","info")
                    unlock_admin_review.apply_async(args=[admin_user.user_id], eta=datetime.now(timezone.utc) + timedelta(hours=24))

                db.session.add(newsysreca)
                db.session.commit()
                flash(f"User {user.email} Approved To Modifiy Patient Record ID {patient_id}!", "success")
                expires_action.apply_async(args=[user_id,patient_id], eta=datetime.now(timezone.utc) + timedelta(minutes=2))
                return redirect(url_for("admin.pending_users"))
            flash("This user lacks the patient instance for approval")
            return redirect(url_for("admin.pending_users"))  
        except Exception:
            logging.exception("Error")
            flash("An error occurred during approval", "danger")
            return redirect(url_for("admin.pending_users"))






@admin_bp.route("/reject/<int:user_id>/<string:patient_id>",methods = ["GET","POST"])
@login_required
def reject_user(user_id,patient_id):
        user = users.query.get(user_id)
        admin_user = users.query.filter_by(user_id = current_user.user_id).first()
        for sysfeatures in admin_user.systab:
            if not sysfeatures:
                logging.info(" No Sysfeatures instance")
                flash("System error occurred", "danger")
                return redirect(url_for("admin.homeadmin"))
        
            if sysfeatures.lock_admin_rejection == 1:
                flash(f"Reject privilleges exceeded:{current_user.firstname} is locked for 24 hours","info")
                return redirect(url_for("admin.homeadmin"))
        
        if not user:
                flash("User not found", "danger")
                return redirect(url_for("admin.homeadmin"))
        
        try:
            index = 0   
            if user.user_update_per_patient == patient_id:
                user.deny = True
                user.user_patient_denied = patient_id
                user.user_id_denied_per_patient = user_id
                user.email_verified = False
                user.update_click = False
                user.useraction_count += 1
                index += 1
                sysfeatures.number_of_admin_rejections += 1
                newsysrec = systab(narration = (f"Date:{datetime.now(timezone.utc)}| Admin user:{current_user.firstname}" 
                                               f" withheld approval for {user.firstname} to perform a sensitive task as part of the ongoing job operation"),
                                    number_of_admin_rejections = sysfeatures.number_of_admin_rejections,
                                    user_sys_id = current_user.user_id
                                    )
                denial_rec = unlock(id_user = user_id,
                                    idx = index,
                                    pid = patient_id)
                
                if sysfeatures.number_of_admin_rejections == 10:
                    sysfeatures.lock_admin_rejection = True
                    unlock_admin_review.apply_async(args=[admin_user.user_id], eta=datetime.now(timezone.utc) + timedelta(minutes=2))
                db.session.add(newsysrec)
                db.session.add(denial_rec)
                db.session.commit()
                denied_user     = user.user_id_denied_per_patient
                pid_denied      = user.user_patient_denied
                expires_action_deny.apply_async(args=[denied_user,pid_denied], eta=datetime.now(timezone.utc) + timedelta(minutes=3))
                flash(f"User {user.email} Request Rejected To Modify Patient Record ID {patient_id}!")
                return redirect(url_for("admin.pending_users"))
            flash("User lacks the patient instance for rejections")
            return redirect(url_for("admin.pending_users"))
        except Exception:
            logging.exception("Error")
            flash("An error occurred", "danger")
            return redirect(url_for("admin.pending_users"))

   


