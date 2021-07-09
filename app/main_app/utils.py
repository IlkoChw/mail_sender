import logging
import re
import requests
from django.core.mail import send_mail, get_connection
from django.utils.html import strip_tags
from django.forms.models import model_to_dict

logger = logging.getLogger(__name__)


def serial_model(model_obj) -> dict:

    """
    :param model_obj: инстанс модели
    :return: словарь со всеми атрибутами объекта
    """

    opts = model_obj._meta.fields
    model_dict = model_to_dict(model_obj)
    for m in opts:
        if m.is_relation:
            foreignkey = getattr(model_obj, m.name)
            if foreignkey:
                try:
                    model_dict[m.name] = serial_model(foreignkey)
                except:
                    pass
    return model_dict


def template_variables_replace(template: str, variables: dict, clear_empty_var=False) -> str:

    """
    :param template: html-шаблон
    :param variables: словарь с переменными для подмены прим. {first_name: 'Ivan', 'last_name': 'Petrov'}
    :param clear_empty_var: флаг для удаления не заменённых переменных
    :return: html-шаблон с заменёнными переменными
    """

    # замена всех доступных переменных в шаблоне
    for key in variables:
        if f'%{key}%' in template:
            template = template.replace(f'%{key}%', variables[key])

    if clear_empty_var:
        # удаление всех оставшихся переменных по регулярному выражению
        pattern = '%[a-zA-Z_\d]+%'
        template = re.sub(pattern, '', template)

    return template


def get_target_subscribers(mailing_instance):
    from .models import Subscriber

    target_subscribers = Subscriber.objects.filter(groups__in=mailing_instance.groups.all()).distinct()
    for target_subscriber in target_subscribers:
        yield target_subscriber


def create_check_letter(letter_model, mailing_instance, subscriber_instance) -> None:
    return letter_model.objects.create(
        _mailing=mailing_instance,
        _subscriber=subscriber_instance,
        _created_by=mailing_instance._created_by)


def get_ngrok_domain() -> [str, None]:
    try:
        return requests.get(f'http://ngrok:4040/api/tunnels').json()['tunnels'][0]['public_url']
    except Exception as e:
        logger.error(f'Не удалось подключиться к ngrok!\n({e})')
        return None


# основная функция для массовой рассылки
def mass_send_email(mailing_pk):
    from .models import Letter, Mailing

    mailing_instance = Mailing.objects.get(pk=mailing_pk)
    logger.info(f'Запуск рассылки {mailing_instance}')

    # бэкенд для рассылки, настройки подтягиваются и mailing_instance
    connection = get_connection(
        host=mailing_instance.created_by.email_host,
        port=mailing_instance.created_by.email_port,
        username=mailing_instance.created_by.email_host_user,
        password=mailing_instance.created_by.email_password,
        use_tls=mailing_instance.created_by.email_use_tls,
        use_ssl=mailing_instance.created_by.email_use_ssl
    )

    # используется только для дебага
    domain = get_ngrok_domain()

    subject = mailing_instance.subject
    template_source = mailing_instance.template.template_source
    if domain is not None and template_source is not None:
        message = strip_tags(template_source)
        subscribers = get_target_subscribers(mailing_instance)
        for subscriber in subscribers:
            try:
                letter = create_check_letter(Letter, mailing_instance, subscriber)

                template_source = template_variables_replace(template_source, subscriber.to_json())
                template_source += f'<img src="{get_ngrok_domain()}{letter.get_absolute_url()}" alt="check">'

                logger.info(f'Отправка сообщения на почту {subscriber.email}')
                send_mail(subject, message, mailing_instance.created_by.email_host_user, [subscriber.email],
                          html_message=template_source, connection=connection)

            except Exception as e:
                logger.error(f'Ошибка отправки на почту {subscriber.email}\n({e})')
    else:
        logger.warning(f'Не удалось создать рассылку')

    connection.close()
