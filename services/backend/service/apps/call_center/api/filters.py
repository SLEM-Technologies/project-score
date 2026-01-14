from django.core import validators
from django_filters import rest_framework as filters

from apps.call_center.consts import (
    FULL_NAME_QUERY_PARAMETER_MAX_LENGTH,
    FULL_NAME_QUERY_PARAMETER_MIN_LENGTH,
)
from apps.call_center.db.models import Client, SMSHistory


class ClientListFilter(filters.FilterSet):
    # search query parameter was defined in views with different queryset

    phone_number = filters.CharFilter(method='phone_number_filter')

    class Meta:
        model = Client
        fields = ('phone_number',)

    def phone_number_filter(self, queryset, name, value):
        return queryset.filter(
            phones__is_primary=True,
            phones__app_number__exact=value,
            phones__extractor_removed_at__isnull=True,
        )


class CharInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class ClientContactedListFilter(filters.FilterSet):
    name = filters.CharFilter(
        lookup_expr='icontains',
        field_name='client__full_name',
        validators=(
            validators.MinLengthValidator(
                limit_value=FULL_NAME_QUERY_PARAMETER_MIN_LENGTH
            ),
            validators.MaxLengthValidator(
                limit_value=FULL_NAME_QUERY_PARAMETER_MAX_LENGTH
            ),
        ),
    )
    sent = filters.DateFromToRangeFilter(field_name='sent_at')
    followed = filters.BooleanFilter(field_name='is_followed')
    practice = CharInFilter(field_name='practice_id', lookup_expr='in')

    class Meta:
        model = SMSHistory
        fields = ('name', 'sent', 'followed', 'practice')
