from flask import Blueprint, render_template, flash, redirect,url_for
from Apex_clinic_app.app_forms import registerform
from Apex_clinic_app.model_mapping import users, admin_token
from Apex_clinic_app.extensions import db
from Apex_clinic_app.celery_backgroud_app_runs import delete_admintoken
from datetime import datetime, timezone,timedelta


main_bp = Blueprint('main', __name__)

@main_bp.route("/")
def mainpage():
    return render_template('mainpage.html')




@main_bp.route("/register", methods = ["GET", "POST"])
def register():
    form = registerform() 
    if form.validate_on_submit():
            Email = form.email.data
            verify_newuser = users.query.filter_by(email=Email).first()
            if verify_newuser:
                flash(f'Oops!User:{Email} already exist!')
                return redirect(url_for('main.register'))
            if form.admin.data == "Yes":
                admin_secrete_token = form.token.data
                verify_token = admin_token.query.filter_by(token = admin_secrete_token).first()
                if not verify_token :
                    flash("Token not found.Please contact system administrator for assistance")
                    return redirect(url_for("main.register"))
                if verify_token.expired_token:
                    flash("Invalid or expired token.Please contact system administrator for assistance")
                    return redirect(url_for("main.register"))
                
                username= form.username.data
                firstname = form.firstname.data
                lastname = form.lastname.data
                password = form.password.data
                new_user=users(firstname = firstname,lastname=lastname,username=username,email = Email, is_admin = True)
                new_user.set_password(password)
                db.session.add(new_user)
                verify_token.expired_token = True
                db.session.commit()
                delete_admintoken.apply_async(args=[admin_secrete_token],eta=datetime.now(timezone.utc) + timedelta(minutes=1))
                flash('User registered successfully','success')
                return redirect(url_for('main.mainpage'))
            
            username= form.username.data
            firstname = form.firstname.data
            lastname = form.lastname.data
            password = form.password.data
            new_user=users(firstname = firstname,lastname=lastname,username=username,email = Email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('User registered successfully','info')
            return redirect(url_for('main.mainpage'))
    return render_template("registeruser.html",form = form)