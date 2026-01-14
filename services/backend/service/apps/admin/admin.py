import re
from typing import Any
from urllib.parse import urlencode

import arrow
from django import forms
from django.contrib import admin
from django.contrib.admin import widgets
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.db import models
from django.db.models import F
from django.http.request import HttpRequest
from django.shortcuts import redirect

from apps.base.constants.errors import SystemMessageEnum
from apps.call_center.db.models import (
    Answer,
    Outcome,
    Practice,
    Question,
    PracticeSettings,
)
from apps.sms.consts import SMS_VARIABLES, MIN_EXPIRY_PERIOD_IN_WEEKS
from apps.sms.db.models import SMSTemplate

User = get_user_model()


class VetSuccessAdminSite(admin.AdminSite):
    site_header = 'Remote Communications Admin Dashboard'
    site_title = 'Remote Communications Admin Dashboard'
    index_title = 'Admin Panel'
    default_filters = {
        User.__name__: '?is_superuser__exact=0',
        Practice.__name__: '?settings=yes',
    }

    def get_app_list(self, request, app_label=None):
        app_list = super().get_app_list(request)
        for app in app_list:
            for model in app['models']:
                if (object_name := model['object_name']) in self.default_filters:
                    model['admin_url'] += self.default_filters[object_name]
        return app_list


vetsuccess_admin_site = VetSuccessAdminSite(name='vetsuccess_admin')


@admin.register(User, site=vetsuccess_admin_site)
class VetSuccessUserAdmin(UserAdmin):
    add_form_template = 'add_form.html'
    actions = None
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        (
            'Permissions',
            {
                'fields': (
                    'is_active',
                    'is_superuser',
                ),
            },
        ),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'password1', 'password2'),
            },
        ),
    )
    readonly_fields = ('last_login', 'created_at', 'updated_at')
    list_display = ('email', 'first_name', 'last_name', 'is_superuser', 'is_active')
    list_filter = ('is_superuser', 'is_active')
    ordering = ('email',)
    search_fields = ('email',)

    def save_model(self, request: Any, obj: Any, form: Any, change: Any) -> None:
        setattr(obj, 'is_staff', getattr(obj, 'is_superuser'))
        return super().save_model(request, obj, form, change)


@admin.register(Outcome, site=vetsuccess_admin_site)
class OutcomeAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.CharField: {
            'widget': widgets.AdminTextareaWidget(attrs={'cols': 80, 'rows': 5})
        },
    }
    fieldsets = (
        (None, {'fields': ('text',)}),
        ('Dates', {'fields': ('created_at', 'updated_at')}),
    )
    readonly_fields = ('created_at', 'updated_at')
    list_display = ('text',)
    ordering = ('text',)
    search_fields = ('text',)


class AnswerInline(admin.StackedInline):
    model = Answer
    extra = 0
    ordering = ('question__text',)
    formfield_overrides = {
        models.CharField: {'widget': widgets.AdminTextareaWidget(attrs={'rows': '3'})},
    }

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        formfield.widget.can_delete_related = False
        return formfield


class PracticeSettingsForm(forms.ModelForm):
    class Meta:
        model = PracticeSettings
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('end_date_for_launch') and not cleaned_data.get('start_date_for_launch'):
            raise forms.ValidationError(
                {'end_date_for_launch': SystemMessageEnum.X0009.value.detail}
            )

        if cleaned_data.get('end_date_for_launch') and cleaned_data.get('start_date_for_launch'):
            if cleaned_data.get('end_date_for_launch') <= cleaned_data.get('start_date_for_launch'):
                raise forms.ValidationError(
                    {'end_date_for_launch': SystemMessageEnum.X0010.value.detail}
                )

        if cleaned_data.get('start_date_for_launch') and cleaned_data.get('launch_date'):
            if cleaned_data.get('start_date_for_launch') >= arrow.get(cleaned_data.get('launch_date')).shift(weeks=-MIN_EXPIRY_PERIOD_IN_WEEKS).date():
                raise forms.ValidationError(
                    {'start_date_for_launch': SystemMessageEnum.X0011.value.detail.format(weeks=MIN_EXPIRY_PERIOD_IN_WEEKS)}
                )
        return cleaned_data


class PracticeSettingsInline(admin.StackedInline):
    form = PracticeSettingsForm
    model = PracticeSettings
    template = 'stacked.html'
    extra = 0
    can_delete = False
    fieldsets = (
        (
            'SMS',
            {
                'fields': (
                    'is_sms_mailing_enabled',
                    'sms_senders_phone',
                    'sms_practice_name',
                    'sms_scheduler',
                    'sms_link',
                    'sms_phone',
                )
            },
        ),
        (
            'Updated data',
            {
                'fields': (
                    'is_email_updates_enabled',
                    'email',
                    'scheduler_email',
                    'rdo_name',
                    'rdo_email',
                )
            },
        ),
        (
            'Launch date',
            {
                'fields': (
                    'launch_date',
                    'start_date_for_launch',
                    'end_date_for_launch',
                )
            },
        ),
    )


class HasPracticeSettingsFilter(admin.SimpleListFilter):
    title = 'Practice Settings'
    parameter_name = 'settings'

    def lookups(self, request, model_admin):
        return [
            ('yes', 'Yes'),
            ('no', 'No'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(settings__isnull=False)
        elif self.value() == 'no':
            return queryset.filter(settings__isnull=True)
        else:
            return queryset


@admin.register(Practice, site=vetsuccess_admin_site)
class PracticeAdmin(admin.ModelAdmin):
    inlines = (PracticeSettingsInline, AnswerInline)
    actions = None
    list_per_page = 50
    fieldsets = (
        (None, {'fields': ('odu_id', 'is_archived',)}),
        (
            'Info',
            {
                'fields': (
                    'name',
                    'address_1',
                    'address_2',
                    'city',
                    'state',
                    'country',
                    'zip_code',
                    'phone',
                )
            },
        ),
        (
            'Server Info',
            {
                'fields': (
                    'get_server_odu_id',
                    'get_server_name',
                )
            },
        ),
        (
            'Important dates',
            {
                'fields': (
                    'practice_updated_at',
                    'latest_extractor_updated',
                    'latest_transaction',
                )
            },
        ),
    )
    readonly_fields = (
        'odu_id',
        'name',
        'address_1',
        'address_2',
        'city',
        'state',
        'country',
        'zip_code',
        'phone',
        'practice_updated_at',
        'latest_extractor_updated',
        'latest_transaction',
        'get_server_name',
        'get_server_odu_id',
    )
    list_display = ('name', 'odu_id', 'city', 'state', 'zip_code', 'phone', 'get_server_odu_id', 'is_archived',)
    list_filter = (
        HasPracticeSettingsFilter,
        'settings__is_sms_mailing_enabled',
        'settings__is_email_updates_enabled',
        'is_archived',
    )
    ordering = ('name',)
    search_fields = ('name', 'odu_id', 'city', 'state', 'zip_code', 'phone')

    def changelist_view(self, request, extra_context=None):
        if 'is_archived__exact' not in request.GET:
            query = request.GET.copy()
            query['is_archived__exact'] = '0'
            return redirect(f"{request.path}?{urlencode(query)}")
        return super().changelist_view(request, extra_context=extra_context)

    def get_server_name(self, obj):
        return obj.server_name
    get_server_name.short_description = 'Server Name'

    def get_server_odu_id(self, obj):
        return obj.server_odu_id
    get_server_odu_id.short_description = 'Server Odu ID'


    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_delete_permission(
        self, request: HttpRequest, obj: Any | None = None
    ) -> bool:
        return False

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            server_name=F('server__name'),
            server_odu_id=F('server__odu_id'),
        )


@admin.register(Question, site=vetsuccess_admin_site)
class QuestionAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.CharField: {'widget': widgets.AdminTextareaWidget(attrs={'rows': '5'})},
    }
    fieldsets = (
        (None, {'fields': ('text',)}),
        ('Dates', {'fields': ('created_at', 'updated_at')}),
    )
    readonly_fields = ('created_at', 'updated_at')
    list_display = ('text',)
    ordering = ('text',)
    search_fields = ('text',)


class SMSTemplatesForm(forms.ModelForm):
    class Meta:
        model = SMSTemplate
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        template = cleaned_data.get('template')
        if template:
            invalid_variables = []
            pattern = r'\{([^}]+)\}'
            matches = re.findall(pattern, template)
            for match in matches:
                if match not in SMS_VARIABLES:
                    invalid_variables.append(match)

            if invalid_variables:
                raise forms.ValidationError(
                    message=SystemMessageEnum.X0008.value.detail.format(
                        variables=', '.join(invalid_variables)
                    )
                )
        return cleaned_data


@admin.register(SMSTemplate, site=vetsuccess_admin_site)
class SMSTemplateAdmin(admin.ModelAdmin):
    form = SMSTemplatesForm
    readonly_fields = ('created_at', 'updated_at')
    list_display = ('key_words', 'template',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['template'].help_text = f"""
        To add a variable use curly braces. Example: Hi {{your_pets}}!
        List of allowed fields: {', '.join(SMS_VARIABLES)}.
        """
        return form
