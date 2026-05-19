from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, SubmitField, BooleanField,MultipleFileField,RadioField,SelectField,SearchField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError,optional


class registerform(FlaskForm):
    username=           StringField("Username:*", validators=[DataRequired()])
    email =             StringField("Email:*", validators=[DataRequired(), Email()])
    firstname =         StringField("FirstName:*", validators=[DataRequired()])
    lastname =          StringField("LastName:*", validators=[DataRequired()])
    admin =             RadioField("Admin?:", choices=[('Yes','Yes'),('No', 'No')],validators=[DataRequired()])
    token =             StringField("Admin Token:*", validators=[optional()])
    password =          PasswordField("Password:*", validators=[DataRequired()])
    confirm_password =  PasswordField("Confirm Password:*", validators=[DataRequired(), EqualTo("password")])
    submit =            SubmitField("Register Now")


class add_ptestresult(FlaskForm):
    patient_id =        StringField("Patient ID:", validators=[DataRequired()])
    disease =           StringField("Disease:",validators=[DataRequired()])
    fever =             RadioField("Fever:",choices=[('Yes','Yes'),('No', 'No')],validators=[DataRequired()])
    cough =             RadioField("Cough:",choices=[('Yes','Yes'),('No', 'No')],validators=[DataRequired()])
    fatigue =           RadioField("Fatigue:",choices=[('Yes','Yes'),('No', 'No')],validators=[DataRequired()])
    difficult_breath =  RadioField("Difficult Breath:",choices=[('Yes','Yes'),('No', 'No')],validators=[DataRequired()])
    age =               IntegerField("Age:",validators=[DataRequired() ])
    gender =            RadioField("Gender:",choices=[('Male','Male'),('Female', 'Female')],validators=[DataRequired()])
    blood_pressure=     SelectField("Blood Pressure:",validators=[DataRequired()],
                                choices=[('','Select'),('Normal','Normal'),('High','High'),('Low','Low')])
    chol_level =        SelectField("Cholesterol Level:", validators=[DataRequired()],
                                choices=[('','Select'),('Normal','Normal'),('High','High'),('Low','Low')])
    outcome =           RadioField("Outcome Variable:", validators=[DataRequired()],
                                choices=[('Positive','Positive'),('Negative', 'Negative')])
    submit1 =           SubmitField("Add Now")


class loginform(FlaskForm):
    identifier =        StringField("Username/Email", validators=[DataRequired()])
    password =          PasswordField("Password", validators=[DataRequired()],render_kw={"Placeholder":"Enter Password"})

    login =             SubmitField("Login")

class reauthenticate_user(FlaskForm):
    passwordA = PasswordField("Password",validators=[DataRequired()],
                              render_kw={"Placeholder":"Enter Password"})
    loginA = SubmitField("Login")

class loaddata(FlaskForm):
    filename = SelectField("Filename To Upload:",validators=[DataRequired()],
                           choices=[("","Select filename"),("CANCER PATIENT DATA","Cancer Patients file"),
                                    ("PATIENT PROFILE DATASET","Patient Profile file")])
    consult = SubmitField("Submit")

class adminform(FlaskForm):
    username=           StringField("Username:", validators=[DataRequired()])
    email =             StringField("Email:", validators=[DataRequired(), Email()])
    name =              StringField("Name:", validators=[DataRequired()])
    password =          PasswordField("Password:", validators=[DataRequired()])
    confirm_password =  PasswordField("Confirm Password:", validators=[DataRequired(), EqualTo("password")])
    submit =            SubmitField("Register Now")