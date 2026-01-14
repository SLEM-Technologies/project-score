import logging
import time

import arrow
from django.conf import settings
from django.db import transaction
from sentry_sdk import capture_exception

from apps.call_center.db.entities.practices import PracticeSettings
from apps.sms.consts import (
    PHONE_CODE,
    SMS_LIMIT_PER_MINUTE,
    SMSEventStatus,
    SMSHistoryStatus,
)
from apps.sms.dataclasses import SMSContext
from apps.sms.db.models import SMSEvent, SMSHistory
from apps.sms.exceptions import (
    SMSExceptionInvalidPracticeNumber,
    SMSExceptionMailingIsDisabled,
    SMSRateLimitException,
    SMSAuthenticationException,
)
from libs.celery.celery import app
from libs.celery.consts import CeleryQueue
from libs.integrations.dialpad.client import CustomDialpadClient
from libs.utils.decorators import retry

logger = logging.getLogger(__package__)


class SMSSendingTask(app.Task):
    name = 'sms_sending'
    queue = CeleryQueue.SMS.value

    @staticmethod
    def _format_phone_number(number: str) -> str:
        return f'{PHONE_CODE}{number}'

    @staticmethod
    def _get_practice_number(practice_id: str) -> str:
        practice_settings = PracticeSettings.objects.get(practice_id=practice_id)

        if not practice_settings.is_sms_mailing_enabled:
            raise SMSExceptionMailingIsDisabled('SMS mailing for practice is disabled')

        practice_number = practice_settings.sms_senders_phone
        if not practice_number:
            raise SMSExceptionInvalidPracticeNumber('Invalid practice number')

        return practice_number

    @retry(exception_to_check=(ConnectionError, TimeoutError), tries=3, delay=5)
    def _send_sms(self, event_context: SMSContext) -> dict:
        """
        Send SMS via Dialpad API.
        
        Only retries transient network errors (ConnectionError, TimeoutError).
        Does NOT retry rate limits (403/429) or authentication failures - those need special handling.
        """
        practice_number = self._get_practice_number(event_context.practice_id)
        if settings.SEND_DIALPAD_SMS:
            sms_client = CustomDialpadClient(settings.DIALPAD_API_TOKEN)
            try:
                return sms_client.sms.send_sms_by_phone_number(
                    from_number=self._format_phone_number(practice_number),
                    to_numbers=[
                        self._format_phone_number(event_context.number_to),
                    ],
                    text=event_context.text,
                )
            except (SMSRateLimitException, SMSAuthenticationException):
                # Don't retry these - they need special handling in run()
                raise
        return {}

    @staticmethod
    def _update_history_record(
        history_event_id: str,
        status: str,
        updated_at,
        response: dict | None = None,
        error_message: str | None = None,
        sent_at=None,
    ):
        SMSHistory.objects.filter(uuid=history_event_id).update(
            status=status,
            response=response,
            sent_at=sent_at,
            error_message=error_message,
            updated_at=updated_at,
        )

    @transaction.atomic
    def run(self, event_uuid: str):
        event = SMSEvent.objects.select_for_update().get(uuid=event_uuid)
        event_context = SMSContext(**event.context)
        now = arrow.utcnow().datetime
        should_delete_event = True
        
        try:
            response = self._send_sms(event_context)
            self._update_history_record(
                history_event_id=event_context.sms_history_id,
                status=SMSHistoryStatus.SENT,
                response=response,
                sent_at=now,
                updated_at=now,
            )
            logger.info(f"Successfully sent SMS {event_context.sms_history_id}")
            
        except SMSRateLimitException as e:
            # Rate limit hit - re-queue for later (don't mark as ERROR)
            logger.warning(f"Rate limit hit for SMS {event_context.sms_history_id}, re-queuing for 5 minutes: {e}")
            
            # Re-schedule event for 5 minutes from now
            event.send_at = arrow.utcnow().shift(minutes=5).datetime
            event.status = SMSEventStatus.PENDING.value
            event.save()
            should_delete_event = False
            
            # Update history to show rate limit (keep as PENDING, not ERROR)
            self._update_history_record(
                history_event_id=event_context.sms_history_id,
                status=SMSHistoryStatus.PENDING.value,
                error_message=f"Rate limited, retrying at {event.send_at}: {str(e)}",
                updated_at=now,
            )
            
            # Signal event manager to back off
            SMSEventPeriodicTask.set_rate_limit_cooldown(minutes=5)
            
        except SMSAuthenticationException as e:
            # Authentication failure - this is critical, needs manual intervention
            logger.error(f"Authentication failed for SMS {event_context.sms_history_id}: {e}")
            self._update_history_record(
                history_event_id=event_context.sms_history_id,
                status=SMSHistoryStatus.ERROR.value,
                error_message=f"AUTH_FAILED: {str(e)}",
                updated_at=now,
            )
            capture_exception(e)
            
        except (SMSExceptionInvalidPracticeNumber, SMSExceptionMailingIsDisabled) as e:
            # Configuration errors - don't retry
            logger.error(f"Configuration error for SMS {event_context.sms_history_id}: {e}")
            self._update_history_record(
                history_event_id=event_context.sms_history_id,
                status=SMSHistoryStatus.ERROR.value,
                error_message=f"CONFIG_ERROR: {str(e)}",
                updated_at=now,
            )
            
        except Exception as e:
            # Other unexpected errors
            logger.error(f"Failed to send SMS {event_context.sms_history_id}: {e}")
            self._update_history_record(
                history_event_id=event_context.sms_history_id,
                status=SMSHistoryStatus.ERROR.value,
                error_message=str(e),
                updated_at=now,
            )
            capture_exception(e)
            
        finally:
            # Only delete event if not re-queued
            if should_delete_event:
                SMSEvent.objects.filter(uuid=event.uuid).delete()


class SMSEventPeriodicTask(app.Task):
    name = 'sms_event_manager'
    queue = CeleryQueue.DEFAULT.value
    
    # Class variable to track rate limit cooldown
    _rate_limit_cooldown_until = None

    @classmethod
    def set_rate_limit_cooldown(cls, minutes: int = 5):
        """Set a cooldown period to avoid hitting rate limits"""
        cls._rate_limit_cooldown_until = arrow.utcnow().shift(minutes=minutes)
        logger.warning(f"Rate limit cooldown set until {cls._rate_limit_cooldown_until}")

    @transaction.atomic
    def run(self) -> None:
        # Check if we're in rate limit cooldown period
        if self._rate_limit_cooldown_until and arrow.utcnow() < self._rate_limit_cooldown_until:
            logger.info(f"In rate limit cooldown until {self._rate_limit_cooldown_until}, skipping SMS batch")
            return
        
        count_events_in_progress = SMSEvent.objects.filter(
            status=SMSEventStatus.IN_PROGRESS.value
        ).count()
        count_to_run = SMS_LIMIT_PER_MINUTE - count_events_in_progress
        
        if count_to_run > 0:
            events_to_run = (
                SMSEvent.objects.select_for_update(skip_locked=True)
                .filter(
                    send_at__lte=arrow.utcnow().datetime,
                    status=SMSEventStatus.PENDING.value,
                )
                .all()[:count_to_run]
            )

            logger.info(f"Processing {len(events_to_run)} SMS events (limit: {SMS_LIMIT_PER_MINUTE}, in progress: {count_events_in_progress})")
            
            for event in events_to_run:
                event.status = SMSEventStatus.IN_PROGRESS.value
                event.save()
                SMSSendingTask().apply_async(kwargs={'event_uuid': str(event.uuid)})
                
                # Add tiny delay between queuing to spread out load
                time.sleep(0.01)  # 10ms delay


app.register_task(SMSEventPeriodicTask)
app.register_task(SMSSendingTask)
