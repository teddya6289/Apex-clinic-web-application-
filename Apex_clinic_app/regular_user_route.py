from Apex_clinic_app.extensions import db,logging
from flask import request,render_template,redirect,url_for, flash,Blueprint
from .model_mapping import  patient, users
from .app_forms import add_ptestresult,registerform
from Apex_clinic_app.app_decorators import email_verification_approval,session
from datetime import timezone,datetime,timedelta
from flask_login import login_required,current_user
from Apex_clinic_app.app_utils import secure_regular_user
from Apex_clinic_app.celery_backgroud_app_runs import expires_action



regular_user_bp = Blueprint('user',__name__)
secure_regular_user(regular_user_bp)

@regular_user_bp.route('/userhomepage')
def userhomepage():
    pat = db.session.query(patient).all()
    if pat:
          pat_id = pat[0].patient_id
    return render_template('regular_user_homepage.html',pid = pat_id)





@regular_user_bp.route('/records',methods=['GET'])
@login_required
def records():
            records_all = patient.query.all()
            try:
                if records_all:
                    return render_template('viewpatientrecord.html',records_all=records_all)
                                
                
                            
                flash("Request not successfully","info")
                return redirect(url_for('user.userhomepage'))
            except Exception as e:            
                flash('Oops! Could not fetch record. Please consult admin', 'danger')
                logging.error(f'Oops! Could not fetch record. Please consult admin\n{e}')
                return redirect(url_for('user.userhomepage'))
    


@regular_user_bp.route('/addpatient/<string:patientID>', methods=['GET','POST'])
@login_required
@email_verification_approval
def addpatient(patientID):

    if not patientID:
       flash("patientID not found") 
    form = add_ptestresult()
    
    if form.validate_on_submit(): 
            patient_ID =    form.patient_id.data
            id         =    patient.query.filter_by(patient_id=patient_ID).first()
            if id:
                flash(f"ID:{patient_ID} already exist")
                return redirect(url_for('user.records'))
            
            Disease=            form.disease.data
            Fever =             form.fever.data
            Cough =             form.cough.data
            Fatigue =           form.fatigue.data
            Difficult_breath = form.difficult_breath.data
            Age =               int(form.age.data)
            Gender =            form.gender.data
            Blood_Pressure =    form.blood_pressure.data
            Cholesterol_Level=  form.chol_level.data
            Outcome_Variable=   form.outcome.data

            new_patient =       patient(patient_id =patient_ID,
                                        Disease=Disease,
                                        Fever=Fever,
                                        Cough=Cough,
                                        Fatigue=Fatigue,
                                        Difficulty_Breath=Difficult_breath,
                                        Age=Age,
                                        Gender=Gender,
                                        Blood_Pressure=Blood_Pressure,
                                        Cholesterol_Level=Cholesterol_Level,
                                        Outcome_Variable=Outcome_Variable
                                        )
            db.session.add(new_patient)
            current_user.email_verified = False
            current_user.update_click = False
            db.session.commit()
            flash(f"ID:{patient_ID} addeded successfully","success")
            logging.info(f"New Patient record added - {id}")
            return redirect(url_for('user.records'))    

    return render_template('Addpatient.html', form = form)





@regular_user_bp.route('/updatepatient/<string:patientID>',methods=['GET','POST'])
@login_required
@email_verification_approval
def updatepatient(patientID):
    
    if patientID:
        try:
            patient_record= patient.query.filter_by(patient_id=patientID).first()
            if  patient_record:
                if request.method == "POST":
                    try:
                                patient_record.Disease =            request.form.get('Disease')
                                patient_record.Fever =              request.form.get('Fever')
                                patient_record.Cough =              request.form.get('Cough')
                                patient_record.Fatigue =            request.form.get('Fatigue')
                                patient_record.Difficult_breath =  request.form.get('Difficulty_Breath')
                                patient_record.Age =                int(request.form.get('Age',0))
                                patient_record.Gender =             request.form.get('Gender')
                                patient_record.Blood_Pressure =     request.form.get('Blood_Pressure')
                                patient_record.Cholesterol_Level =  request.form.get('Cholesterol_Level')
                                patient_record.Outcome_Variable =   request.form.get('Output_Variable')
                                db.session.commit()
                                flash(f"Patient record with ID:{patientID} updated successfully.","success")
                                return redirect(url_for('user.records'))
                    except Exception as e:
                            db.session.rollback()
                            logging.error(f" An error occured why updating patient record: {e}")
                            return redirect(url_for('user.records'))
        except Exception as e:
             flash("Error")
             logging.error(f"Record update failed - {e}")
                             
    return render_template('viewpatientrecord.html',patient=patient_record, patientID=patientID)
        



@regular_user_bp.route('/deleterecord/<string:patientID>',methods=['GET','POST'])
@login_required
@email_verification_approval
def deleterecord(patientID):
    flash(f"Request approved. Proceed to delete record.", "success")
    if patientID:
        patient_record = patient.query.filter_by(patient_id=patientID).first()
        if patient_record:
                    db.session.delete(patient_record)
                    db.session.commit()
                    flash(f'Patient:{patientID} record deleted successfully', 'success')
                    expires_action.apply_async(args=[current_user.user_id,patientID], eta=datetime.now(timezone.utc) + timedelta(seconds=5))
                    return redirect(url_for('user.records'))
            
        flash(f'Patient: {patientID} record could not be deleted.Consult Admin!', 'danger')
        return redirect(url_for('user.records'))
            
    return render_template('confirmdelete.html',ID=patientID)




 

