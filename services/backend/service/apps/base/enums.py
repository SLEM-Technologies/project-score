import enum


class BaseEnum(enum.Enum):
    """
    Base enum class.

    Sample of usage:
        class Enum(BaseEnum):
            NEW = 0
            APPROVED = 1
            DECLINED = 2
    """

    @classmethod
    def get_values(cls):
        return [var.value for var in cls]

    @classmethod
    def get_choices(cls):
        return [(var.value, var.name) for var in cls]
