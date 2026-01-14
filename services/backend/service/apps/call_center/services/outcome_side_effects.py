from apps.call_center.db.entities.patients import Patient
from apps.sms.consts import SMSHistoryStatus
from apps.sms.db.models import SMSHistory


class OutcomeSideEffectsService:
    def __init__(self, updated_patients: list[Patient]):
        self.updated_patients = updated_patients
        self.updated_patient_ids = [patient.odu_id for patient in updated_patients]

    def _get_sms_records(self) -> list[SMSHistory]:
        return SMSHistory.objects.prefetch_related(
            'reminders__patient',
        ).filter(
            status=SMSHistoryStatus.SENT.value,
            is_followed=False,
            reminders__patient_id__in=self.updated_patient_ids
        ).distinct()

    def _is_all_patients_checked(self, sms_record: SMSHistory) -> bool:
        patients_from_sms_record = [reminder.patient for reminder in sms_record.reminders.all()]
        not_updated_patients = [
            patient
            for patient in patients_from_sms_record
            if patient.odu_id not in self.updated_patient_ids
        ]
        if not not_updated_patients:
            return True

        return all([
            patient.outcome_at and patient.outcome_at >= sms_record.sent_at
            for patient in not_updated_patients
        ])

    def follow_up_sent_sms(self):
        sms_records = self._get_sms_records()
        for sms_record in sms_records:
            if self._is_all_patients_checked(sms_record):
                sms_record.is_followed = True
                sms_record.save()
