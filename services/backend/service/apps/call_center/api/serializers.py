import uuid

import arrow
from dateutil.relativedelta import relativedelta
from django.db import transaction
from rest_framework import serializers

from apps.base.constants.errors import SystemMessageEnum
from apps.base.exceptions import ProjectValidationError
from apps.call_center.consts import ReminderStatus, APPOINTMENT_DATE_FORMAT
from apps.call_center.db.entities.reminders import Appointment, Reminder
from apps.call_center.db.models import (
    Client,
    Email,
    Outcome,
    Patient,
    Phone,
    SMSHistory,
)
from apps.call_center.services.outcome_side_effects import OutcomeSideEffectsService
from apps.sms.consts import PERIOD_TO_DISPLAY_REMINDERS_IN_YEARS, SMSHistoryStatus


class ClientListQueryParamsSerializer(serializers.Serializer):
    search = serializers.CharField(required=False)
    phone_number = serializers.CharField(required=False, min_length=10, max_length=10)

    def validate(self, attrs):
        if len(attrs) != 1:
            raise ProjectValidationError(detail=SystemMessageEnum.X0002.value)
        return attrs


class ClientListSerializer(serializers.ModelSerializer):
    email_address = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = (
            'odu_id',
            'first_name',
            'last_name',
            'full_name',
            'email_address',
            'phone_number',
        )

    def get_email_address(self, obj):
        return obj.prefetched_emails[0].address if obj.prefetched_emails else None

    def get_phone_number(self, obj):
        return obj.prefetched_phones[0].app_number if obj.prefetched_phones else None


class AppointmentSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(read_only=True, format=APPOINTMENT_DATE_FORMAT, source='appointment_datetime')

    class Meta:
        model = Appointment

        fields = ('date',)


class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder

        fields = (
            'date_due',
            'description',
            'sms_status',
        )


class ClientPatientsSerializer(serializers.ModelSerializer):
    patient_age = serializers.SerializerMethodField()
    odu_id = serializers.CharField(required=False, max_length=255)
    next_appointments = serializers.SerializerMethodField()
    last_appointment = serializers.SerializerMethodField()
    reminders = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        read_only_fields = (
            'species_description',
            'breed_description',
            'gender_description',
            'name',
            'patient_age',
            'outcome_at',
            'next_appointments',
            'last_appointment',
            'reminders',
        )
        fields = (
            'odu_id',
            'species_description',
            'breed_description',
            'gender_description',
            'name',
            'patient_age',
            'outcome',
            'opt_out',
            'comment',
            'outcome_at',
            'next_appointments',
            'last_appointment',
            'reminders',
        )

    def validate_outcome(self, value):
        outcomes = Outcome.objects.values_list('text', flat=True)
        if value is not None and value not in outcomes:
            raise ProjectValidationError(SystemMessageEnum.X0003.value)
        return value

    def get_patient_age(self, obj: Patient) -> int | None:
        if obj.birth_date:
            return relativedelta(arrow.utcnow().datetime.date(), obj.birth_date).years

    @transaction.atomic
    def update(self, instance, validated_data):
        old_outcome = instance.outcome
        outcome = validated_data.get('outcome')
        instance = super().update(instance, validated_data)
        if outcome is not None and old_outcome != outcome:
            instance.outcome_at = arrow.now().datetime
            instance.save()
        return instance

    def get_last_appointment(self, obj: Patient) -> dict | None:
        now = arrow.utcnow().date()
        for appointment in obj.prefetched_appointments:
            if appointment.appointment_datetime.date() < now:
                return AppointmentSerializer(appointment).data
        return None

    def get_next_appointments(self, obj: Patient) -> list[dict]:
        now = arrow.utcnow().date()
        appointments_to_return = []
        for appointment in obj.prefetched_appointments:
            if appointment.appointment_datetime.date() >= now:
                appointments_to_return.append(appointment)
        return AppointmentSerializer(appointments_to_return, many=True).data

    def get_reminders(self, obj: Patient) -> list[dict]:
        reminders_to_return = []
        seen = set()
        date_from = arrow.utcnow().shift(years=-PERIOD_TO_DISPLAY_REMINDERS_IN_YEARS).date()

        for reminder in reversed(list(obj.prefetched_reminders)):
            if reminder.date_due >= date_from:
                key = (
                    reminder.practice_id,
                    reminder.client_id,
                    reminder.patient_id,
                    reminder.date_due,
                    reminder.description,
                )
                if key not in seen:
                    seen.add(key)
                    reminders_to_return.append(reminder)

        return ReminderSerializer(reminders_to_return, many=True).data


class ClientPhoneSerializer(serializers.ModelSerializer):
    odu_id = serializers.CharField(required=False, max_length=255)
    set_is_primary = serializers.BooleanField(required=False, write_only=True)

    class Meta:
        model = Phone
        fields = (
            'odu_id',
            'app_number',
            'set_is_primary',
        )


class ClientEmailSerializer(serializers.ModelSerializer):
    odu_id = serializers.CharField(required=False, max_length=255)
    set_is_primary = serializers.BooleanField(required=False, write_only=True)

    class Meta:
        model = Email
        fields = (
            'odu_id',
            'address',
            'set_is_primary',
        )


class ClientDetailSerializer(serializers.ModelSerializer):
    practices = serializers.SerializerMethodField()
    emails = ClientEmailSerializer(many=True, source='prefetched_emails')
    phones = ClientPhoneSerializer(many=True, source='prefetched_phones')
    patients = ClientPatientsSerializer(many=True, source='prefetched_patients')

    class Meta:
        model = Client
        fields = (
            'odu_id',
            'first_name',
            'last_name',
            'full_name',
            'emails',
            'phones',
            'practices',
            'patients',
        )

    def get_practices(self, obj: Client) -> list[dict] | None:
        practices = list(obj.server.practices.values('odu_id', 'name'))
        if len(practices) == 1:
            return practices

        # Optimize: Fix N+1 query + inefficient algorithm
        # Change from O(n²) list comprehension to O(n) set lookup
        practice_ids_set = {p['odu_id'] for p in practices}  # O(n) conversion
        sms_history = SMSHistory.objects.filter(
            status=SMSHistoryStatus.SENT.value,
            practice__is_archived=False,
            client=obj,
        ).order_by('-sent_at').first()
        if sms_history and sms_history.practice_id in practice_ids_set:  # O(1) lookup
            return [p for p in practices if p['odu_id'] == sms_history.practice_id]

        return practices


class ClientDetailUpdateSerializer(serializers.ModelSerializer):
    email = ClientEmailSerializer(write_only=True)
    phone = ClientPhoneSerializer(write_only=True)
    patients = ClientPatientsSerializer(many=True, write_only=True)

    class Meta:
        model = Client
        fields = (
            'first_name',
            'last_name',
            'email',
            'phone',
            'patients',
        )

    @staticmethod
    def _get_instance_by_odu_id(
        odu_id: str, instance_list: list[Phone] | list[Email] | list[Patient]
    ) -> Phone | Email | Patient | None:
        for instance in instance_list:
            if instance.odu_id == odu_id:
                return instance

    @staticmethod
    def _update_instance(
        instance: Phone | Email | Patient,
        payload: dict,
        serializer_class,
    ):
        if payload:
            payload['updated_at'] = arrow.utcnow()
        serializer = serializer_class(instance, data=payload)
        serializer.is_valid(raise_exception=True)
        serializer.update(instance, payload)

    @staticmethod
    def _update_instances_to_set_non_primary(
        instance: Phone | Email, prefetched_instances: list[Phone] | list[Email]
    ):
        for prefetched_instance in prefetched_instances:
            if prefetched_instance != instance:
                prefetched_instance.is_primary = False
                prefetched_instance.save(update_fields=['is_primary', 'updated_at'])

    def _update_email_address(self, client: Client, email_address_payload: dict):
        if email_address_payload:
            if odu_id := email_address_payload.pop('odu_id', None):
                email = self._get_instance_by_odu_id(
                    odu_id=odu_id, instance_list=client.prefetched_emails
                )

                if not email:
                    raise ProjectValidationError(
                        SystemMessageEnum.X0001.value, field='email'
                    )

                set_is_primary = email_address_payload.pop('set_is_primary', None)
                self._update_instance(
                    instance=email,
                    payload=email_address_payload,
                    serializer_class=ClientEmailSerializer,
                )

                if set_is_primary:
                    self._update_instances_to_set_non_primary(
                        instance=email, prefetched_instances=client.prefetched_emails
                    )

            elif not client.prefetched_emails:
                Email.objects.create(
                    address=email_address_payload['address'],
                    odu_id=uuid.uuid4().hex,
                    server_id=client.server_id,
                    client_id=client.odu_id,
                    is_primary=True,
                )

    def _update_phone_number(self, client: Client, phone_number_payload: dict):
        if phone_number_payload:
            if odu_id := phone_number_payload.pop('odu_id', None):
                phone_number = self._get_instance_by_odu_id(
                    odu_id=odu_id, instance_list=client.prefetched_phones
                )
                if not phone_number:
                    raise ProjectValidationError(
                        SystemMessageEnum.X0001.value, field='phone'
                    )
                set_is_primary = phone_number_payload.pop('set_is_primary', None)
                self._update_instance(
                    instance=phone_number,
                    payload=phone_number_payload,
                    serializer_class=ClientPhoneSerializer,
                )
                if set_is_primary:
                    self._update_instances_to_set_non_primary(
                        instance=phone_number,
                        prefetched_instances=client.prefetched_phones,
                    )

            elif not client.prefetched_phones:
                Phone.objects.create(
                    app_number=phone_number_payload['app_number'],
                    odu_id=uuid.uuid4().hex,
                    server_id=client.server_id,
                    client_id=client.odu_id,
                    is_primary=True,
                )

    def _update_patients(self, client: Client, patients_payload: list[dict]):
        patients_to_handle_outcome_update = []
        if patients_payload:
            for patient_payload in patients_payload:
                if odu_id := patient_payload.pop('odu_id', None):
                    patient = self._get_instance_by_odu_id(
                        odu_id=odu_id, instance_list=client.prefetched_patients
                    )
                    if not patient:
                        raise ProjectValidationError(
                            SystemMessageEnum.X0001.value, field='patients'
                        )

                    if 'outcome' in patient_payload:
                        patients_to_handle_outcome_update.append(patient)

                    self._update_instance(
                        instance=patient,
                        payload=patient_payload,
                        serializer_class=ClientPatientsSerializer,
                    )

                    if patients_to_handle_outcome_update:
                        OutcomeSideEffectsService(
                            updated_patients=patients_to_handle_outcome_update
                        ).follow_up_sent_sms()

    @transaction.atomic
    def update(self, instance, validated_data):
        email_address_payload = validated_data.pop('email', None)
        phone_number_payload = validated_data.pop('phone', None)
        patients_payload = validated_data.pop('patients', None)
        self._update_email_address(instance, email_address_payload)
        self._update_phone_number(instance, phone_number_payload)
        self._update_patients(instance, patients_payload)

        # if empty, do not update the updated_at field
        if validated_data:
            return super().update(instance, validated_data)
        else:
            return instance


class FAQListSerializer(serializers.Serializer):
    question = serializers.CharField(source='question.text')
    answer = serializers.CharField(source='text')


class PracticeListSerializer(serializers.Serializer):
    odu_id = serializers.CharField(source='practice_id')
    name = serializers.CharField(source='practice.name')
    scheduler = serializers.CharField(source='practice.settings.sms_scheduler')


class SMSPatientSerializer(serializers.Serializer):
    odu_id = serializers.CharField(source='patient.odu_id')
    name = serializers.CharField(source='patient.name')


class ClientContactedListSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='client.full_name')
    sms_history_id = serializers.CharField(source='uuid')
    practice_name = serializers.CharField(source='practice.name')
    emails = ClientEmailSerializer(many=True, source='client.prefetched_emails')
    phones = ClientPhoneSerializer(many=True, source='client.prefetched_phones')
    patients = SMSPatientSerializer(
        many=True, source='prefetched_reminders'
    )

    class Meta:
        model = SMSHistory
        fields = (
            'client_id',
            'full_name',
            'practice_id',
            'practice_name',
            'sent_at',
            'sms_history_id',
            'is_followed',
            'emails',
            'phones',
            'patients',
        )
