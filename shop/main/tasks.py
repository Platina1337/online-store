from __future__ import absolute_import, unicode_literals
import logging
from celery import shared_task
from django.core.mail import send_mail

logger = logging.getLogger(__name__)

@shared_task
def email_send_message(email):
    subject = 'СКИДКИ 10000%, ВСЕ БЕСПЛАТНО!!!'
    message = 'СКИДОК НЕТ'
    logger.info(f'Attempting to send email to {email}')
    try:
        mail_sent = send_mail(subject, message, 'admin@myshop.com', [email])
        logger.info(f'Email send status: {mail_sent}')
    except Exception as e:
        logger.error(f'Failed to send email to {email}: {e}')
    return mail_sent