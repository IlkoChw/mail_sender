from .utils import mass_send_email
from mail_sender.celery import app as celery_app


@celery_app.task
def task_mass_mailing(mailing_pk):
    mass_send_email(mailing_pk)

