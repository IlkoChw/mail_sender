from django.http import HttpResponseRedirect
from django.http import Http404
from .models import Letter


# просто редиректит на админку
def redirect_to_admin(request):
    return HttpResponseRedirect('/admin/')


# проверка письма на открытие
# при открытии письма, почтовый клиент прогружает картинку по ссылке с уникальным идентификатором
# у экземпляра письма выполняется метод, меняющий флаг opened на True
# Метод проверки на открытие не может быть 100% гарантией того, что юзер открыл письмо
# т.к. почтовые клиенты могут вырезать ссылки и html-теги

def check_opened_letter(request, letter_uuid):
    try:
        letter = Letter.objects.get(_uuid=letter_uuid)
        letter.open_letter()
        return HttpResponseRedirect('/static/check.bmp/')
    except Letter.DoesNotExist:
        raise Http404("Letter does not exist")
