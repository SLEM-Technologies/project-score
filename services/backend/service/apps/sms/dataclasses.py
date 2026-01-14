from dataclasses import dataclass, field

from apps.call_center.db.models import Reminder


@dataclass
class SMSContext:
    number_from: str
    number_to: str
    practice_id: str
    sms_history_id: str
    text: str


@dataclass
class SMSData:
    number_to: str = ''
    sms_history_id: str = ''
    patient_names: list[str] = field(default_factory=list)
    reminders: list[Reminder] = field(default_factory=list)
    patient_has_multiple_reminders: bool = False
