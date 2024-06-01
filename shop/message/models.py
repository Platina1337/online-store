from django.db import models
from django.urls import reverse
from main.models import Profile
from django.utils import timezone

class Dialog(models.Model):
    member_to = models.ForeignKey(Profile, verbose_name="Участник начавший диалог", on_delete=models.CASCADE, related_name='dialogs_started')
    member_from = models.ForeignKey(Profile, verbose_name="Участник с которым начали диалог", on_delete=models.CASCADE, related_name='dialogs_received')
    created_at = models.DateTimeField('Дата создания', default=timezone.now)

    def __str__(self):
        return f'Dialog {self.pk}'

    def get_absolute_url(self):
        return reverse('message:dialogs_view', args=[self.pk])

class Message(models.Model):
    chat = models.ForeignKey(Dialog, verbose_name="Чат", on_delete=models.CASCADE)
    author = models.ForeignKey(Profile, verbose_name="Пользователь", on_delete=models.CASCADE)
    message = models.TextField("Сообщение")
    pub_date = models.DateTimeField('Дата сообщения', default=timezone.now)
    is_readed = models.BooleanField('Прочитано', default=False)

    class Meta:
        ordering = ['pub_date']

    def __str__(self):
        return self.message