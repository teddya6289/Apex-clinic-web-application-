from urllib.parse import urlparse, urljoin
from flask import request, url_for, redirect,flash,current_app,session,abort
from itsdangerous import URLSafeTimedSerializer
from functools import wraps
from flask_login import current_user, logout_user
from Apex_clinic_app.extensions import db
from datetime import datetime, timezone
from Apex_clinic_app.model_mapping import syscarrier


def is_safe_url(target):
    ref_url = urlparse(request.host_url)  # Your app's base URL
    test_url = urlparse(urljoin(request.host_url, target))  # Full URL of target
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def get_safe_redirect(target, default):
    if target and is_safe_url(target):
        return redirect(target)
    return redirect(url_for(default))


def getserializer():
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

def generate_verification_token(Email):
            serializer = getserializer()
            return serializer.dumps(Email, salt='email-verification')

def verify_token(token, expiration=6000):
            serializer = getserializer()
            try:
                email = serializer.loads(token, salt='email-verification', max_age=expiration)
                return email
            except:
                return None
                

def admin_route_secured(a_bp):
    @a_bp.before_request
    def secure_admin_user_routes():
        if not current_user.is_authenticated and not current_user.is_admin:
            abort(404)
        return

def secure_regular_user(r_user_bp):
    @r_user_bp.before_request
    def secure_user_routes():
        if current_user.is_authenticated and not current_user.is_admin:
            return
        abort(404)




def logout_inactive_user(app):
    @app.before_request
    def session_timeout():

        PUBLIC_ENDPOINTS = {
        "main.mainpage",
        "auth.login",
        "main.register",
        "auth.resignin",
        "auth.signout",
        "static"}
        
        if not request.endpoint:
            return

        if request.endpoint in PUBLIC_ENDPOINTS:
            return

        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))
        now = datetime.now(timezone.utc)
        last_active = current_user.last_active.astimezone(timezone.utc)
       
        inactive_seconds = (now - last_active).total_seconds()

        if inactive_seconds >= current_app.config['INACTIVE_SESSION_TIME']:
            if not session.get("reauth_required"):
                session["reauth_required"] = True
                session["reauth_started_at"] = now
                session["userlastpage"] = request.path
                flash("Session expired due to inactivity.","info")
                return redirect(url_for("auth.resignin"))
        
        WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

        if request.method in WRITE_METHODS:
            current_user.last_active = now
            db.session.commit()
        

        

