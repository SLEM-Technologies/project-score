from django.db import models


DATE_FORMAT_TO_GET_FILES = 'YYYY/MM/DD'
FILE_EXTENSION = '.xlsx'
FILENAME_PREFIX = 'Remote_Scheduling'
FILENAME_DATE_FORMAT = 'MMDDYYYY'
MIME_TYPE = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

class UpdatesEmailEventStatus(models.TextChoices):
    NO_FILES = 'NO_FILES'
    PENDING = 'PENDING'
    SENT = 'SENT'
    ERROR = 'ERROR'


DAILY_UPDATES_BODY = '''
Hello,
Please find attached the file{plural_value} with daily updates and changes to be made within your Practice Management System.
Thanks.
'''
DAILY_UPDATES_SUBJECT = 'Daily updates from Remote Scheduling team'
