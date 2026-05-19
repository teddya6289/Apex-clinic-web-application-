from Apex_clinic_app.celeryconfig import celery
from celery.schedules import crontab


celery.conf.beat_schedule = {
    "autoupload1":{
        "task": "incremental_upload",
        "schedule": crontab(hour = 0, minute = 0,day_of_week='sun'),
        "args":("Cancer_Patient_Data.xlsx",),
        },
    
    "autoupload2":{"task": "incremental_upload",
        "schedule": crontab(hour = 0, minute = 0, day_of_week='sun'),
        "args":("Patient_Profile_Dataset.csv",),
        }
    }