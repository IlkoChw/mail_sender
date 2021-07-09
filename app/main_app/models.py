from django.db import models
from django.db.models.signals import post_save
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.dispatch import receiver
from django.core.validators import FileExtensionValidator
from django.shortcuts import reverse
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django_currentuser.db.models import CurrentUserField

from ckeditor.fields import RichTextField

from .tasks import task_mass_mailing
from .utils import serial_model
from .managers import CustomUserManager

import uuid


# Переопределенная модель пользователя
# Помимо аутентификации, она используется для хранения настроем почты с которой происходит рассылка
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    email_host = models.CharField(max_length=100, blank=True)
    email_port = models.PositiveIntegerField(null=True, blank=True)
    email_host_user = models.EmailField(blank=True)
    email_password = models.CharField(max_length=50, blank=True)
    email_use_tls = models.BooleanField(default=True, blank=True)
    email_use_ssl = models.BooleanField(default=False, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class PermissionAbstractModel(models.Model):
    _created_by = CurrentUserField(editable=False)

    class Meta:
        abstract = True

    @property
    def created_by(self):
        return self._created_by


class SubscriberGroup(PermissionAbstractModel):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name


class Subscriber(PermissionAbstractModel):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    email = models.EmailField()
    groups = models.ManyToManyField(SubscriberGroup, related_name="subscribers")

    def __str__(self):
        return f'{self.email} ({self.last_name} {self.first_name})'

    def to_json(self):
        return serial_model(self)


class HtmlTemplate(PermissionAbstractModel):
    name = models.CharField(max_length=100)
    body = RichTextField(blank=True)
    file = models.FileField(upload_to='html_templates', blank=True, validators=[FileExtensionValidator(['html'])])

    def __str__(self):
        return self.name

    # тело шаблона выбирается в зависимости от того, какие поля заполнены
    # в приоритете поле body, если оно пустое, проверяем file
    # если файл загружен, то читаем из него данные и возвращаем
    # если ни одно поле не заполнено, возвращаем None

    @property
    def template_source(self):
        if self.body:
            return self.body
        elif self.file:
            with open(f'./{self.file.url}') as src:
                return src.read()
        else:
            return None


class Mailing(PermissionAbstractModel):
    subject = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    template = models.ForeignKey(HtmlTemplate, related_name='template', on_delete=models.CASCADE)
    groups = models.ManyToManyField(SubscriberGroup)
    time_of_sending = models.DateTimeField()
    created = models.DateTimeField(default=timezone.now)
    task_created = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return self.description


@receiver(post_save, sender=Mailing)
def create_mailing_task(sender, instance, created, **kwargs):

    # создаем задание на рассылку если не установлен флаг task_created
    # если текущее время больше либо равно time_of_sending, создаем задание сразу
    # иначе отправляем в то время, которое указано в time_of_sending

    if not instance.task_created:
        task_mass_mailing.delay(instance.pk)
        if timezone.now() >= instance.time_of_sending:
            task_mass_mailing.delay(instance.pk)
        else:
            countdown = (instance.time_of_sending - timezone.now()).total_seconds()
            task_mass_mailing.apply_async((instance.pk, ), countdown=countdown)
        instance.task_created = True
        instance.save()


class Letter(PermissionAbstractModel):
    _uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    _mailing = models.ForeignKey(Mailing, related_name='mailing', editable=False, on_delete=models.CASCADE)
    _subscriber = models.ForeignKey(Subscriber, related_name='subscriber', editable=False, on_delete=models.CASCADE)
    opened = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return f'Letter {self.pk}'

    @property
    def uuid(self):
        return self._uuid

    @property
    def mailing(self):
        return self._mailing

    @property
    def subscriber(self):
        return self._subscriber

    def get_absolute_url(self):
        return reverse('check_opened_letter', kwargs={'letter_uuid': self.uuid})

    def open_letter(self):
        if not self.opened:
            self.opened = True
            self.save()
