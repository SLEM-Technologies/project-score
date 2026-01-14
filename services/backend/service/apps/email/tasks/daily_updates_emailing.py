import io
import logging
from collections import defaultdict

import arrow
from azure.storage.blob import BlobServiceClient
from django.conf import settings
from django.db.models import Prefetch
from libs.utils.holidays import USHolidaysWithoutBlackFriday

from apps.call_center.db.entities.practices import Practice, PracticeSettings
from apps.call_center.db.entities.servers import Server
from apps.email.consts import (
    DATE_FORMAT_TO_GET_FILES,
    FILE_EXTENSION,
    FILENAME_PREFIX,
    FILENAME_DATE_FORMAT,
    MIME_TYPE,
    UpdatesEmailEventStatus,
)
from apps.email.dataclasses import EmailAttachmentProperty
from apps.email.db.models import UpdatesEmailEvent
from apps.email.exceptions import (
    DailyUpdatesExceptionInvalidPracticeEmail,
)
from apps.email.services.email import EmailSendingService
from libs.celery.celery import app
from libs.celery.consts import CeleryQueue
from libs.storage.blob import get_blob_service_client

logger = logging.getLogger(__package__)


class CreateDailyUpdatesEmailEventsPeriodicTask(app.Task):
    name = 'daily_updates_manager'
    queue = CeleryQueue.EMAIL

    def run(self):
        if not self._is_work_day():
            return {'message': 'Today is not a working day'}

        servers = self._get_servers()
        blob_service_client = get_blob_service_client()
        server_files_map = self._get_server_files_map(blob_service_client)
        for server in servers:
            file_paths = server_files_map.get(str(server.odu_id))
            for practice in server.prefetched_practices:
                event = self._create_event(file_paths, practice)
                if file_paths:
                    SendDailyUpdatesEmailTask().apply_async(kwargs={'event_id': str(event.uuid)})

    @staticmethod
    def _get_servers():
        return Server.objects.prefetch_related(
            Prefetch(
                'practices',
                queryset=Practice.objects.filter(
                    settings__is_email_updates_enabled=True,
                    is_archived=False,
                ),
                to_attr='prefetched_practices',
            ),
        ).filter(
            practices__settings__is_email_updates_enabled=True
        ).distinct()

    @staticmethod
    def _create_event(file_paths: list[str], practice: Practice) -> UpdatesEmailEvent:
        return UpdatesEmailEvent.objects.create(
            status=(
                UpdatesEmailEventStatus.PENDING.value if file_paths
                else UpdatesEmailEventStatus.NO_FILES.value
            ),
            file_paths=file_paths if file_paths else [],
            practice=practice,
        )

    @staticmethod
    def _is_work_day() -> bool:
        next_workday = USHolidaysWithoutBlackFriday(years=arrow.now().year)._get_next_workday(
            arrow.now().shift(days=-1).datetime
        )
        return next_workday.date() == arrow.now().date()

    @staticmethod
    def _get_previous_work_day() -> arrow.Arrow:
        holidays_class = USHolidaysWithoutBlackFriday(years=arrow.now().year)
        previous_date = arrow.now().shift(days=-1)
        while True:
            if previous_date.date() in holidays_class or holidays_class._is_weekend(previous_date.date()):
                previous_date = previous_date.shift(days=-1)
            else:
                return previous_date

    def _get_date_range_to_check_files(self) -> list[str]:
        previous_work_day = self._get_previous_work_day()
        yesterday = arrow.now().shift(days=-1)
        return [
            previous_work_day.shift(days=i).format(DATE_FORMAT_TO_GET_FILES)
            for i in range((yesterday - previous_work_day).days + 1)
        ]

    @staticmethod
    def _is_valid_file_path(path: str) -> bool:
        parts = path.split('/')
        return parts and len(parts) == 6 and parts[-1].endswith(FILE_EXTENSION)

    def _get_server_files_map(self, blob_service_client: BlobServiceClient) -> dict[str, list[str]]:
        server_files_map = defaultdict(list)
        container_client = blob_service_client.get_container_client(settings.UPDATES_CONTAINER_NAME)
        for date_to_check in self._get_date_range_to_check_files():
            for path in container_client.list_blob_names(
                name_starts_with=f'{settings.UPDATES_PATH_PREFIX}/{date_to_check}'
            ):
                if self._is_valid_file_path(path):
                    parts = path.split('/')
                    server_id = parts[-2]
                    server_files_map[server_id].append(path)

        return dict(server_files_map)


class SendDailyUpdatesEmailTask(app.Task):
    name = 'daily_updates_email'
    queue = CeleryQueue.EMAIL

    autoretry_for = (Exception,)
    max_retries = 3
    retry_backoff = 3

    def run(self, event_id: str) -> None:
        event = UpdatesEmailEvent.objects.get(uuid=event_id)
        attachment_to_send: list[EmailAttachmentProperty] = []

        try:
            practice_settings = self._get_practice_settings(event)
            blob_service_client = get_blob_service_client()
            for file_path in event.file_paths:
                file_name = f'{FILENAME_PREFIX}_{self._get_date_from_file_path(file_path)}'
                file_data = self._get_data(
                    file_path=file_path,
                    blob_service_client=blob_service_client,
                )

                attachment_to_send.append(
                    EmailAttachmentProperty(
                        filename=f'{file_name}{FILE_EXTENSION}',
                        content=file_data,
                        mimetype=MIME_TYPE
                    )
                )

            EmailSendingService.send_daily_updates(
                to_email=practice_settings.email,
                attachments=attachment_to_send,
                cc_emails=self._get_cc_emails(practice_settings)
            )

        except Exception as e:
            event.status = UpdatesEmailEventStatus.ERROR.value
            event.error_message = str(e)
            event.save()
            raise e

        event.status = UpdatesEmailEventStatus.SENT.value
        event.save()

    @staticmethod
    def _get_cc_emails(practice_settings: PracticeSettings) -> tuple:
        cc_emails = []
        if practice_settings.rdo_email:
            cc_emails.append(practice_settings.rdo_email)
        if practice_settings.scheduler_email:
            cc_emails.append(practice_settings.scheduler_email)
        return tuple(cc_emails)

    @staticmethod
    def _get_practice_settings(event: UpdatesEmailEvent) -> PracticeSettings:
        practice_settings = event.practice.settings

        if not practice_settings.email:
            raise DailyUpdatesExceptionInvalidPracticeEmail('Invalid practice email')

        return practice_settings

    @staticmethod
    def _get_date_from_file_path(file_path: str) -> str:
        date_str = '/'.join(file_path.split('/')[1:4])
        return arrow.get(date_str, DATE_FORMAT_TO_GET_FILES).format(FILENAME_DATE_FORMAT)

    @staticmethod
    def _get_data(
        file_path: str,
        blob_service_client: BlobServiceClient,
    ) -> bytes:

        blob_client = blob_service_client.get_blob_client(
            container=settings.UPDATES_CONTAINER_NAME,
            blob=file_path
        )

        with io.BytesIO() as in_memory_buffer:
            blob_client.download_blob().readinto(in_memory_buffer)
            in_memory_buffer.seek(0)
            downloaded_data = in_memory_buffer.getvalue()
        return downloaded_data


app.register_task(CreateDailyUpdatesEmailEventsPeriodicTask)
app.register_task(SendDailyUpdatesEmailTask)
