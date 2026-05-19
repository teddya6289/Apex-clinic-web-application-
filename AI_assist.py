from flask import current_app, redirect, render_template,url_for,abort, Blueprint,request
from flask_login import current_user, login_required
from Apex_clinic_app.app_functions import generate_insight
from Apex_clinic_app.model_mapping import patient
from Apex_clinic_app.extensions import logging




Aiassist_bp = Blueprint('Ai', __name__)


@Aiassist_bp.route("/AiSupport/<string:pid>",methods=["GET","POST"])
@login_required
def AiSupport(pid):
    if pid:
        try:
            Patient = patient.query.filter_by(patient_id=pid).first()
            if not patient:
                return "Patient record not found"
            if request.method == "POST":
                KPI_data = {"Disease":Patient.Disease,
                            "Fever?":Patient.Fever,
                            "Cough?":Patient.Cough,
                            "Fatigue?":Patient.Fatigue,
                            "Difficulty Breathing?":Patient.Difficult_breath,
                            "Age":Patient.Age,
                            "Gender":Patient.Gender,
                            "Blood Pressure":Patient.Blood_Pressure,
                            "Cholesterol Level":Patient.Cholesterol_Level
                            }
                AiSupport_MedicalReport = generate_insight(KPI_data)
        except Exception:
            logging.exception("AI support encounter error")
    return render_template("AiSupport.html", AiReport = AiSupport_MedicalReport)
