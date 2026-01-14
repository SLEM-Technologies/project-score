import datetime
import logging
import uuid
from dataclasses import asdict
from typing import Generator, Iterable, Iterator, Literal, Type

import arrow
import pytz
from django.db import transaction
from django.db.models import Model, Prefetch, Q
from libs.celery.celery import app
from libs.celery.consts import CeleryQueue
from libs.utils.holidays import USHolidaysWithoutBlackFriday

from apps.call_center.consts import ReminderStatus
from apps.call_center.db.models import (
    Appointment,
    Client,
    Patient,
    Phone,
    Practice,
    Reminder,
)
from apps.sms.consts import (
    CREATE_BATCH_SIZE,
    MAX_EXPIRY_PERIOD_IN_YEARS,
    MIN_EXPIRY_PERIOD_IN_WEEKS,
    PATIENTS_CHUNK_SIZE,
    PHONE_TYPES_TO_EXCLUDE,
    SEND_AT_HOUR,
    DEFAULT_SMS_TEMPLATE_W_LINK,
    DEFAULT_SMS_TEMPLATE_W_PHONE,
    UPDATE_BATCH_SIZE,
    SMS_TIME_ZONE,
    OUTCOMES_TO_FILTER_OUT,
)
from apps.sms.dataclasses import SMSContext, SMSData
from apps.sms.db.models import SMSEvent, SMSHistory, SMSTemplate

logger = logging.getLogger(__package__)


class SMSEventCreationSubtaskLaunchPeriodicTask(app.Task):
    name = 'sms.event_creation_subtask_launch'
    queue = CeleryQueue.DEFAULT

    def run(self) -> None:
        practices = Practice.objects.filter(
            settings__is_sms_mailing_enabled=True,
            is_archived=False,
        ).values_list('odu_id', flat=True)
        for practice_id in practices:
            SMSEventCreationTask().apply_async(kwargs={'practice_id': practice_id})


class SMSEventCreationTask(app.Task):
    name = 'sms.event_creation'
    queue = CeleryQueue.DEFAULT

    # Messages for this task will be acknowledged **after**
    # the task has been executed, and not *right before* (the
    # default behavior).
    #
    # This means the task may be executed twice if the worker
    # crashes mid execution. It will be ok, this task is idempotent.
    acks_late = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.practice = None
        self.launch_date = None

    def run(self, practice_id: str) -> None:
        logger.info("start sms event creation")
        self.practice = Practice.objects.select_related('settings').get(
            odu_id=practice_id
        )
        self.launch_date = self.practice.settings.launch_date
        self._process_reminders()

    def _process_reminders(self) -> None:
        patients_mapping: dict[str, SMSData] = {}
        patients = self._get_patients_iterator()
        reminders_to_update = []
        
        logger.info("start processing reminders")
        for patient in patients:
            reminders = patient.prefetched_reminders
            appointments = patient.prefetched_appointments
            if appointments and appointments[0].appointment_datetime.date() >= reminders[
                0
            ].date_due - datetime.timedelta(weeks=2):
                reminders_to_update.extend(
                    self._update_objs(
                        reminders, sms_status=ReminderStatus.APPOINTMENT_EXISTS
                    )
                )
            elif not patient.prefetched_clients:
                reminders_to_update.extend(
                    self._update_objs(
                        reminders, sms_status=ReminderStatus.NO_ACTIVE_CLIENT
                    )
                )
            else:
                client = patient.prefetched_clients[0]
                if not client.prefetched_phones:
                    reminders_to_update.extend(
                        self._update_objs(reminders, sms_status=ReminderStatus.NO_PHONE)
                    )
                    continue
                phone_number = client.prefetched_phones[0]
                if phone_number.type in PHONE_TYPES_TO_EXCLUDE:
                    reminders_to_update.extend(
                        self._update_objs(
                            reminders, sms_status=ReminderStatus.EXCLUDED_PHONE_TYPE
                        )
                    )
                else:
                    sms_data = patients_mapping.setdefault(client.odu_id, SMSData())
                    patient_name = (
                        patient.name.title() if patient.name else patient.name
                    )
                    sms_data.patient_names.append(patient_name)
                    sms_data.number_to = phone_number.app_number
                    sms_data.reminders.append(reminders[0])
                    if len(reminders) > 1:
                        sms_data.patient_has_multiple_reminders = True
                    reminders_to_update.extend(
                        self._update_objs(
                            reminders[1:], sms_status=ReminderStatus.CHECKED
                        )
                    )
            if len(reminders_to_update) >= UPDATE_BATCH_SIZE - 50:
                self._run_bulk_update(
                    model=Reminder, objs=reminders_to_update, fields=['sms_status']
                )
                reminders_to_update = []

        self._run_bulk_update(
            model=Reminder, objs=reminders_to_update, fields=['sms_status']
        )
        if patients_mapping:
            self._create_and_update_sms_entities(patients_mapping)

    def _get_patients_iterator(self) -> Iterator[Patient]:
        logger.info("get patients")
        return (
            Patient.objects.filter(
                Q(name__isnull=False),
                Q(reminders__practice=self.practice),
                Q(reminders__sms_status__isnull=True),
                Q(reminders__extractor_removed_at__isnull=True),
                self._get_date_lookup('reminders__date_due'),
                ~Q(pims_is_deceased=True),
                ~Q(pims_is_inactive=True),
                ~Q(pims_is_deleted=True),
                ~Q(pims_has_suspended_reminders=True),
                ~Q(is_deceased=True),
                Q(death_date__isnull=True),
                Q(extractor_removed_at__isnull=True),
                Q(euthanasia_date__isnull=True),
                ~Q(outcome__in=OUTCOMES_TO_FILTER_OUT),
            )
            .distinct('odu_id')
            .prefetch_related(
                Prefetch(
                    'clients',
                    queryset=Client.objects.filter(
                        ~Q(pims_is_inactive=True),
                        ~Q(pims_is_deleted=True),
                        ~Q(pims_has_suspended_reminders=True),
                        ~Q(is_home_practice=False),
                        Q(extractor_removed_at__isnull=True),
                        relationships__extractor_removed_at__isnull=True,
                    )
                    .only('odu_id')
                    .order_by('-relationships__is_primary', 'odu_id')
                    .prefetch_related(
                        Prefetch(
                            'phones',
                            queryset=Phone.objects.filter(
                                is_primary=True,
                                app_number__isnull=False,
                                extractor_removed_at__isnull=True,
                            )
                            .only('odu_id', 'client', 'type', 'app_number')
                            .order_by('odu_id'),
                            to_attr='prefetched_phones',
                        )
                    ).distinct(),
                    to_attr='prefetched_clients',
                ),
                Prefetch(
                    'reminders',
                    queryset=Reminder.objects.filter(
                        self._get_date_lookup('date_due'),
                        practice=self.practice,
                        sms_status__isnull=True,
                        extractor_removed_at__isnull=True,
                    )
                    .only('odu_id', 'patient', 'practice', 'date_due', 'description')
                    .order_by('-date_due'),
                    to_attr='prefetched_reminders',
                ),
                Prefetch(
                    'appointments',
                    queryset=Appointment.objects.filter(
                        ~Q(is_canceled_appointment=True),
                        extractor_removed_at__isnull=True,
                    )
                    .only('odu_id', 'patient', 'appointment_datetime')
                    .order_by('-appointment_datetime'),
                    to_attr='prefetched_appointments',
                ),
            )
            .only('odu_id', 'name')
            .iterator(chunk_size=PATIENTS_CHUNK_SIZE)
        )

    def _get_date_lookup(self, field_name: str) -> Q:
        if self.launch_date == arrow.utcnow().date():
            settings = self.practice.settings
            if settings.start_date_for_launch and settings.end_date_for_launch:
                start = settings.start_date_for_launch
                end = settings.end_date_for_launch
            elif settings.start_date_for_launch:
                start = settings.start_date_for_launch
                end = arrow.utcnow().shift(weeks=-MIN_EXPIRY_PERIOD_IN_WEEKS).date()
            else:
                start = arrow.utcnow().shift(years=-MAX_EXPIRY_PERIOD_IN_YEARS).date()
                end = arrow.utcnow().shift(weeks=-MIN_EXPIRY_PERIOD_IN_WEEKS).date()
            return Q(
                **{f'{field_name}__range': (start, end)}
            )
        else:
            return Q(
                **{
                    f'{field_name}': arrow.utcnow()
                    .shift(weeks=-MIN_EXPIRY_PERIOD_IN_WEEKS)
                    .date()
                }
            )

    def _create_and_update_sms_entities(
        self, patients_mapping: dict[str, SMSData]
    ) -> None:
        logger.info("start create and update sms entities")
        sms_events_to_create = []
        sms_histories_to_create = []
        reminders_to_update = []
        for client_id, sms_data in patients_mapping.items():
            sms_data.sms_history_id = str(uuid.uuid4())
            context = SMSContext(
                number_from=self.practice.settings.sms_senders_phone,
                number_to=sms_data.number_to,
                practice_id=self.practice.odu_id,
                sms_history_id=sms_data.sms_history_id,
                text=self._create_sms_text(sms_data),
            )
            sms_history = SMSHistory(
                uuid=sms_data.sms_history_id,
                practice_id=self.practice.odu_id,
                client_id=client_id,
                event_context=asdict(context),
            )
            sms_events_to_create.append(
                SMSEvent(
                    send_at=self._get_send_at(),
                    context=asdict(context),
                )
            )
            sms_histories_to_create.append(sms_history)
            reminders_to_update.extend(
                self._update_objs(
                    sms_data.reminders,
                    sms_history=sms_history,
                    sms_status=ReminderStatus.EVENT_CREATED,
                )
            )

        self._run_bulk_methods(
            sms_events_to_create, sms_histories_to_create, reminders_to_update
        )

    def _create_sms_text(self, sms_data: SMSData) -> str:
        your_pets_capitalized, your_pets, be_verb = (
            *self._concat_names(sms_data.patient_names),
        )
        template = (
            self._get_template(sms_data.reminders)
            if not sms_data.patient_has_multiple_reminders
            else DEFAULT_SMS_TEMPLATE_W_LINK
        )
        return template.format(
            scheduler=self.practice.settings.sms_scheduler,
            practice_name=self.practice.settings.sms_practice_name,
            your_pets_capitalized=your_pets_capitalized,
            your_pets=your_pets,
            be_verb=be_verb,
            link=self.practice.settings.sms_link,
            practice_phone_number=self.practice.settings.sms_phone,
        )

    @staticmethod
    def _get_template(reminders: list[Reminder]) -> str:
        templates: list[str] = []
        sms_templates: dict[tuple[str, ...], str] = SMSTemplate.get_values_dict()
        for reminder in reminders:
            if not reminder.description:
                return DEFAULT_SMS_TEMPLATE_W_LINK
            description = reminder.description.lower()
            for key_words, template in sms_templates.items():
                is_break = False
                for word in key_words:
                    if word in description:
                        templates.append(template)
                        is_break = True
                        break
                if is_break:
                    break
            else:
                return DEFAULT_SMS_TEMPLATE_W_LINK
        if len(templates) > 1:
            return DEFAULT_SMS_TEMPLATE_W_PHONE
        return templates[0]

    @staticmethod
    def _concat_names(
        names: list[str],
    ) -> tuple[str, str, Literal['is'] | Literal['are']]:
        if len(names) == 1:
            pet_names_begin = pet_names_end = names[0]
            be_verb = 'is'
        elif len(names) <= 3:
            pet_names_begin = pet_names_end = (
                ', '.join(names[:-1]) + f' and {names[-1]}'
            )
            be_verb = 'are'
        else:
            pet_names_begin = 'Your pets'
            pet_names_end = 'your pets'
            be_verb = 'are'
        return pet_names_begin, pet_names_end, be_verb

    @staticmethod
    def _get_send_at():
        '''
        Calculate the next scheduled send time based on the current date and time settings.

        Warning:
            The method, by default, determines the same day as when it's executed. If you
            need to schedule the send time for the next day, adjust the shift value.
        '''
        next_workday = USHolidaysWithoutBlackFriday(years=arrow.now().year)._get_next_workday(
            arrow.now().shift(days=-1).datetime
        )
        time_send_at = datetime.time(
            hour=SEND_AT_HOUR, tzinfo=pytz.timezone(SMS_TIME_ZONE)
        )
        return (
            arrow.get(datetime.datetime.combine(next_workday.date(), time_send_at))
            .to(pytz.UTC)
            .datetime
        )

    @staticmethod
    def _update_objs(objs: list[Reminder], **kwargs) -> Generator[Reminder, None, None]:
        for obj in objs:
            for attr, value in kwargs.items():
                setattr(obj, attr, value)
            obj.updated_at = arrow.utcnow().datetime
            yield obj

    @transaction.atomic
    def _run_bulk_methods(
        self,
        sms_events: list[SMSEvent],
        sms_history: list[SMSHistory],
        reminders: list[Reminder],
    ) -> None:
        logger.info("create sms events")
        SMSEvent.objects.bulk_create(sms_events, batch_size=CREATE_BATCH_SIZE)
        
        logger.info("create sms history")
        SMSHistory.objects.bulk_create(sms_history, batch_size=CREATE_BATCH_SIZE)
        
        self._run_bulk_update(Reminder, reminders, ['sms_status', 'sms_history'])

    @staticmethod
    def _run_bulk_update(
        model: Type[Model], objs: Iterable[Model], fields: list[str]
    ) -> None:
        logger.info("update reminders")
        fields.append('updated_at')
        model.objects.bulk_update(objs, fields, batch_size=UPDATE_BATCH_SIZE)


app.register_task(SMSEventCreationSubtaskLaunchPeriodicTask)
app.register_task(SMSEventCreationTask)
