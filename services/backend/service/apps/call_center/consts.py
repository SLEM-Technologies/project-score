from django.db import models

CLIENTS_CONTACTED_SET_PAGINATION_DEFAULT_LIMIT = 10
CLIENTS_CONTACTED_SET_PAGINATION_MAX_LIMIT = 100
FULL_NAME_QUERY_PARAMETER_MIN_LENGTH = 3
FULL_NAME_QUERY_PARAMETER_MAX_LENGTH = 511

SHEDULER_DROPDOWN_TEMPLATE = 'View {}\'s Practices'

APPOINTMENT_DATE_FORMAT = '%Y-%m-%d'


class ReminderStatus(models.TextChoices):
    CHECKED = 'CHECKED', 'Checked and passed as redundant'
    EVENT_CREATED = 'EVENT_CREATED', 'Created SMS Event'
    NO_PHONE = (
        'NO_PHONE',
        'Checked and passed due to missing primary phone number',
    )
    NO_ACTIVE_CLIENT = (
        'NO_ACTIVE_CLIENT',
        'Checked and passed due to lack of active client',
    )
    EXCLUDED_PHONE_TYPE = (
        'EXCLUDED_PHONE_TYPE',
        'Checked and passed as the phone type is in the list of excluded phone types',
    )
    APPOINTMENT_EXISTS = (
        'APPOINTMENT_EXISTS',
        'There is an appointment with a date after the last date_due reminder.',
    )
