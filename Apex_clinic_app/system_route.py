from Apex_clinic_app.extensions import db,logging
from Apex_clinic_app.model_mapping import users
from Apex_clinic_app.app_forms import loaddata
from flask import Blueprint, render_template,redirect, url_for, flash,session
from flask_login import login_required,current_user
from datetime import datetime, timezone
from Apex_clinic_app.app_functions import rawfilename,datatransformed,load_data
from sqlalchemy import or_







sys_bp = Blueprint('sys', __name__)

@sys_bp.route('/syshomepage')
def syshomepage():
    return render_template('sys_homepage.html')


@sys_bp.route('/admins',methods = ["GET","POST"])
@login_required
def admins():
            app_users = users.query.filter(or_(users.is_admin == True,users.is_admin == False)).all()
            try:
                return render_template('appusers.html', app_users = app_users)
            except Exception:
                        logging.exception('Error')
                        flash("Request not successfully")
                        return redirect(url_for('sys.syshomepage'))




@sys_bp.route("/scheduleload", methods = ["GET","POST"])
@login_required
def scheduleload():
    conn = db.engine.raw_connection()
    lform = loaddata()
    if lform.validate_on_submit():
            file_to_upload = lform.filename.data
            if file_to_upload:
                    filename = rawfilename(file_to_upload)
                    csvfilename,df = datatransformed(filename)
                    try:
                        response = load_data(conn,df,csvfilename)
                        flash(response)
                    except Exception as e:
                        flash (response)
    return render_template("loadpage.html", form = lform)

