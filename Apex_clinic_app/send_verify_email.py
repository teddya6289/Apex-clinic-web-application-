
from Apex_clinic_app.extensions import mail,db,logging
from flask import request,render_template,redirect,url_for, flash,Blueprint,session,abort
from .model_mapping import  users
from sqlalchemy import or_
from Apex_clinic_app.app_utils import generate_verification_token,verify_token,get_safe_redirect
from flask_login import login_required,current_user,logout_user
from flask_mail import Message


send_verify_email_bp = Blueprint('ev',__name__)

@send_verify_email_bp.route('/sendemail/<string:pid>', methods=['GET'])
@login_required
def sendemail(pid):
                email =     current_user.email
                if not email:
                            flash("Required data is missing. Please try again.")
                            logging.info(f"User email not found - {current_user.user}")
                
                
                token = generate_verification_token(email)
                verification_url = url_for('ev.verifyEmail',patientID=pid,token=token, _external=True)

                subject = "Verify Your Email"
                body = f"""
                        <p> An attempt was initiated to update a patient record.</p>
                        <p> To proceed click the link <a href = "{verification_url}"> Verify Email </a></p>
                        <p> If you did not initiated this request, Please ignore the message. Thank you</p>
                        """
                try:
                    msg = Message(subject=subject,sender='no-reply@example.com',recipients=[email], html=body)
                    mail.send(msg)
                    flash(f"Email Verification Required :link have been sent","success")
                    db.session.commit()
                    return redirect(url_for('user.userhomepage'))
                    
                
                except Exception as e:
                    flash(f"Failed to send verification email")
                    logging.error(f"Failed to send verification email - {e}")
                    return redirect(url_for('user.userhomepage'))
                
    
        
       
@send_verify_email_bp.route('/verifyEmail//<string:patientID>/<token>', methods = ['GET', 'POST'])
def verifyEmail(token,patientID):
            email = verify_token(token)
            if not email:
                    flash ("Verification link is invalid or has expired.", "danger")
                    logging.error(f"Broken email verification link - {current_user.id}")
                    return redirect(url_for('auth.login'))
            if current_user.is_authenticated:
                                        user=users.query.filter_by(email=email).first()
                                        if user:
                                            user.email_verified = True
                                            user.update_click = True
                                            user.user_update_per_patient = patientID
                                            db.session.commit()
                                            flash("Email verified successfully!")
                                            logging.info(f"Email verification succeeded - {current_user.user_id}")
                                            next_page = session.pop('clickedroute',None)
                                            if next_page:
                                                return get_safe_redirect(next_page, 'auth.login')

                                        else:
                                            flash("User not found", "danger")
                                            return redirect(url_for('user.records'))
                        
            return render_template('verifyEmail.html', email = email)
                
                        
