import os
import pandas as pd
from Apex_clinic_app.extensions import logging
from flask import flash






def rawfilename(filename):
    if not isinstance(filename,str):
        filename = str(filename)
    if filename.startswith("CANCER"):
        rawfile = "_".join(filename.title().split())+".xlsx"
    else:
        rawfile = "_".join(filename.title().split())+".csv"     
    return rawfile




def datatransformed(filename):
    path = os.path.abspath('/Apex_clinic_app/clinic_record')
    fullpath    = os.path.join(path,filename) 
    if filename.startswith("Cancer"):
        dataset = pd.read_excel(fullpath)
        df = dataset.copy()
    else:
        dataset = pd.read_csv(fullpath)
        df = dataset.copy()
    
    numeric_cols = df.select_dtypes(include="number").columns
    object_cols = df.select_dtypes(include="object").columns
    df=df.dropna(subset=numeric_cols)
    df=df.dropna(subset=object_cols)
    return filename,df        






def load_data(conn,df,filename):
        cursor = conn.cursor()
        cursor.fast_executemany = True
        rows = [tuple(x) for x in df.itertuples(index = False, name = None)]
        try:
            if filename == "Cancer_Patient_Data.xlsx":
                cursor.execute("{CALL bulk_load_medical_facts (?)}", (rows,))
            else:
                cursor.execute("{CALL upsert_diagnosis (?)}", (rows,))
            conn.commit()
            logging.info(f'Records loaded successfully into {"CANCER PATIENT TABLE" if filename == "Cancer_Patient_Data.xlsx" else "PATIENT PROFILE TABLE"}')   
            return "Loading command executed successfully"
        except Exception as e:
            conn.rollback()
            logging.error(f"Error loading file into data:\n{e}")
            return ("Error loading file")
        finally:
            cursor.close()
            conn.close()



def read_secret(path):
    with open(path, "r") as f:
        return f.read().strip()







def generate_insight(data):
    from openai import OpenAI
    import os
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    with open("Ai_prompts.txt") as f:
        template = f.read()

    prompt = template.format(data=data)

    response = client.responses.create(
        model="gpt-4.1",
        input=prompt
    )

    return response.output_text
    


                
