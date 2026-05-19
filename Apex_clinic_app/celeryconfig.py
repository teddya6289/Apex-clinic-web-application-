from celery import Celery
from Apex_clinic_app import creatapp


def init_celery(app):
    celery = Celery(app.import_name,broker=app.config["REDIS_URL_QUEUE"],backend=app.config["REDIS_URL_STORE"])
    celery.conf.update(app.config)
    celery.conf.timezone = "America/Edmonton"
    celery.conf.enable_utc = True
    celery.autodiscover_tasks([app.import_name])
    celery.set_default()

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


application = creatapp()
celery = init_celery(application)