from rest_framework.exceptions import ValidationError

from apps.base.constants.errors import SystemMessage


class ProjectValidationError(ValidationError):
    """
    The base custom ValidationError class
    that takes the usual argument 'detail' and the argument
    based on the SystemMessage dataclass.
    """

    def __init__(self, detail, code=None, **kwargs):
        if isinstance(detail, SystemMessage):
            message = {
                'detail': detail.detail.format(**kwargs)
            }
            if detail.title:
                message['title'] = detail.title.format(**kwargs)
        elif isinstance(detail, str):
            message = {'detail': detail.format(**kwargs)}
        else:
            message = detail
        super().__init__(message, code)
