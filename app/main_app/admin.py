from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .admin_filters import FilterUserAdmin
from .models import SubscriberGroup, Subscriber, HtmlTemplate, Mailing, Letter, CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm


admin.site.site_header = 'Mail sender'


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ('email', 'is_staff', 'is_active',)
    list_filter = ('email', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')},),
        ('Email settings', {'fields': (
            'email_host', 'email_port', 'email_host_user', 'email_password', 'email_use_tls', 'email_use_ssl')},)
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
         ),
    )
    search_fields = ('email',)
    ordering = ('email',)


admin.site.register(CustomUser, CustomUserAdmin)


@admin.register(SubscriberGroup)
class SubscriberGroupAdmin(FilterUserAdmin):
    list_display = ('__str__', )


@admin.register(Subscriber)
class SubscriberAdmin(FilterUserAdmin):
    list_display = ('__str__', )
    filter_horizontal = ('groups', )
    readonly_fields = ('created_by', )


@admin.register(HtmlTemplate)
class HtmlTemplateAdmin(FilterUserAdmin):
    list_display = ('__str__', )
    readonly_fields = ('created_by', )


@admin.register(Mailing)
class MailingAdmin(FilterUserAdmin):
    list_display = ('__str__', )
    filter_horizontal = ('groups', )
    readonly_fields = ('created_by', )


@admin.register(Letter)
class LetterAdmin(FilterUserAdmin):
    list_display = ('__str__', 'mailing', 'subscriber', 'opened')
    list_filter = ('_mailing', 'opened')
    readonly_fields = ('uuid', 'mailing', 'subscriber', 'created_by')
