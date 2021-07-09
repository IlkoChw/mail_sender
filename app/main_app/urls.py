from django.urls import path
from .views import redirect_to_admin, check_opened_letter

urlpatterns = [
    path('', redirect_to_admin, name='redirect_to_admin'),
    path('letter/<letter_uuid>', check_opened_letter, name='check_opened_letter'),
]
