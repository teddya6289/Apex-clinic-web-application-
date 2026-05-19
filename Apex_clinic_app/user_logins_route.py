from Apex_clinic_app.extensions import db,logging
from flask import request,render_template,redirect,url_for, flash,Blueprint,session,abort
from .model_mapping import users, syscarrier
from .app_forms import loginform,reauthenticate_user
from sqlalchemy import or_ ,and_
from datetime import timezone,datetime
from Apex_clinic_app.app_utils import get_safe_redirect,current_app
from flask_login import login_required,login_user,logout_user,current_user


users_bp = Blueprint('auth',__name__)



@users_bp.route('/login',methods=['GET','POST'])
def login():
    form = loginform()
    if form.validate_on_submit():
            
                Email_Username =    form.identifier.data
                Password =          form.password.data
                if Email_Username.endswith("Apsys1@Apexclinic.com"):
                        try:
                            sysaccess = syscarrier.query.filter_by(email=Email_Username).first()
                            if sysaccess and sysaccess.check_password(Password):
                                if sysaccess.is_sys:
                                    logout_user()
                                    session.clear()
                                    login_user(sysaccess)
                                    sysaccess.last_active =  datetime.now(timezone.utc)
                                    db.session.commit()
                                    flash(f"log in successful","success")
                                    logging.info(f"User log in successfully - {sysaccess.sys_name}")
                                    next_page = request.args.get('next')
                                    return get_safe_redirect(next_page, 'sys.syshomepage')
                                abort(401)
                            return redirect(url_for('auth.login'))
                        except Exception as e:
                            flash(f"Log in failed re-check log in details","danger")
                            logging.error(f"Log in failed re-check log in details - {e}")
                
                user = users.query.filter(or_(users.email==Email_Username,users.username == Email_Username)).first()
                try:
                    if user and user.check_password(Password):
                        if user.is_admin:
                            logout_user()
                            session.clear()
                            login_user(user)
                            user.last_active =  datetime.now(timezone.utc)
                            db.session.commit()
                            flash(f"log in successful","success")
                            logging.info(f"User log in successfully - {user.username}")
                            next_page = request.args.get('next')
                            return get_safe_redirect(next_page, 'admin.homeadmin')
                        logout_user()
                        session.clear()
                        login_user(user)
                        user.last_active =  datetime.now(timezone.utc)
                        db.session.commit()
                        flash("log in successful","success")
                        logging.info(f"User log in successfully - {user.username}")
                        next_page = request.args.get('next')
                        return get_safe_redirect(next_page, 'user.userhomepage')
                    flash("User not found","info")
                    return redirect(url_for('auth.login'))
                except Exception as e:
                    flash(f"Log in failed re-check log in details","danger")
                    logging.error(f"Log in failed re-check log in details - {e}")
    return render_template('login.html', form = form)




@users_bp.route('/resignin',methods=['GET','POST'])
def resignin():
    form = reauthenticate_user()
   
    if not current_user.is_authenticated:
         return redirect(url_for("auth.login"))
    
    if not session.get('reauth_required'):
        return redirect(url_for('main.mainpage'))
    user_email=current_user.email
    now=datetime.now(timezone.utc)
    reauth_started = session.get("reauth_started_at")
    if not reauth_started:
        logout_user()
        session.clear()
        return redirect(url_for("auth.login"))
       
    
    inactive_seconds = (now - reauth_started).total_seconds()
    if inactive_seconds >= current_app.config['RESIGNIN_GRACEPERIOD']:
            flash('inactive session logged out completely','info')
            session.clear()
            logout_user()
            return redirect(url_for('main.mainpage'))
            
    if form.validate_on_submit():
                try:
                    Password = form.passwordA.data
                    if current_user.check_password(Password):
                            session.pop('reauth_required', None)
                            next_page = session.pop('userlastpage', None)
                            session.pop("reauth_started_at",None)
                            current_user.last_active =  datetime.now(timezone.utc)
                            db.session.commit()
                            flash("Reauthenticated successful")
                            if next_page and current_user.is_sys:
                                        return get_safe_redirect(next_page,'sys.syshomepage')
                            if next_page and current_user.is_admin:
                                return get_safe_redirect(next_page,'admin.homeadmin')
                            else:
                                return get_safe_redirect(next_page,'user.userhomepage')

                    flash("Incorrect password", "danger")
                    return redirect(url_for('auth.resignin'))
                except Exception:
                    flash("Authentication failed re-check your details","danger")
                    logging.exception(f"Reuthentication failed re-check your details")
    return render_template('inactivesession.html',form=form,currentuser_email=user_email)
           


@users_bp.route('/signout')
@login_required
def signout():
    session.clear()
    logout_user()
    
    flash("You have been logged out.", "info")

    return redirect(url_for('main.mainpage'))