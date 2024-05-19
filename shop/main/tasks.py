from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.core.mail import send_mail

@shared_task
def email_send_message(email):
    subject = 'СКИДКИ 10000%, ВСЕ БЕСПЛАТНО!!!'
    message = 'СКИДОК НЕТ'
    mail_sent = send_mail(subject, message, 'admin@myshop.com', [email])
    return mail_sent