from django.conf import settings
from django.core.mail import EmailMessage

from apps.email.consts import DAILY_UPDATES_BODY, DAILY_UPDATES_SUBJECT
from apps.email.dataclasses import EmailAttachmentProperty


class EmailSendingService:
    @classmethod
    def _get_recipients(cls, to: tuple[str]) -> tuple[str]:
        return (settings.DEBUG_RECIPIENT,) if settings.USE_DEBUG_EMAIL else to

    @classmethod
    def _get_cc_recipients(cls, cc: tuple[str]) -> tuple[str]:
        return (settings.DEBUG_CC_RECIPIENT,) if settings.USE_DEBUG_EMAIL else cc

    @classmethod
    def send(
        cls,
        to: tuple[str],
        body: str = '',
        subject: str = '',
        attachments: list[EmailAttachmentProperty] | None = None,
        cc: tuple[str] | None = None
    ):
        message = EmailMessage(
            subject=subject,
            body=body,
            to=cls._get_recipients(to),
            from_email=f'{settings.DEFAULT_FROM_EMAIL}',
            cc=cls._get_cc_recipients(cc)
        )

        for attachment in attachments:
            message.attach(
                filename=attachment.filename,
                content=attachment.content,
                mimetype=attachment.mimetype,
            )

        message.send()

    @classmethod
    def send_daily_updates(cls, to_email: str, attachments: [EmailAttachmentProperty], cc_emails: tuple[str]):
        cls.send(
            to=(to_email,),
            body=DAILY_UPDATES_BODY.format(plural_value='s' if len(attachments) > 1 else ''),
            subject=DAILY_UPDATES_SUBJECT,
            attachments=attachments,
            cc=cc_emails,
        )
