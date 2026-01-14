from dataclasses import dataclass

from apps.base.enums import BaseEnum


@dataclass
class SystemMessage:
    detail: str
    title: str = None


class SystemMessageEnum(BaseEnum):
    X0001 = SystemMessage(
        detail='Invalid odu_id for {field} field.'
    )
    X0002 = SystemMessage(
        detail='You can specify one query parameter.'
    )
    X0003 = SystemMessage(
        detail='Invalid outcome value.'
    )
    X0004 = SystemMessage(
        detail='The phone number must consist of 10 digits.'
    )
    X0005 = SystemMessage(
        detail=(
            'It is not allowed to activate SMS Mailing if at least one of the '
            'fields is empty.'
        )
    )
    X0007 = SystemMessage(
        detail=(
            'You cannot activate sending updates if the email field is empty.'
        )
    )
    X0008 = SystemMessage(
        detail=(
            '{variables} variables are not supported in the template.'
        )
    )
    X0009 = SystemMessage(
        detail=(
            'Two date fields must be filled in.'
        )
    )
    X0010 = SystemMessage(
        detail=(
            'Start date must be less than end date.'
        )
    )
    X0011 = SystemMessage(
        detail=(
            'Start date must be less than launch date minus {weeks} weeks.'
        )
    )

