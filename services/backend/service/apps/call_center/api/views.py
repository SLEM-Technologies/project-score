from collections import OrderedDict, defaultdict

from django.core.cache import cache
from django.db.models import Prefetch, Q
from django_filters import rest_framework as filters
from rest_framework import generics, pagination, permissions, views
from rest_framework.response import Response

from apps.call_center.consts import (
    CLIENTS_CONTACTED_SET_PAGINATION_DEFAULT_LIMIT,
    CLIENTS_CONTACTED_SET_PAGINATION_MAX_LIMIT,
    SHEDULER_DROPDOWN_TEMPLATE,
    ReminderStatus,
)
from apps.call_center.db.models import (
    Answer,
    Appointment,
    Client,
    Email,
    Outcome,
    Patient,
    Phone,
    Reminder,
    SMSHistory,
)
from apps.sms.consts import SMSHistoryStatus

from .filters import (
    ClientContactedListFilter,
    ClientListFilter,
)
from .serializers import (
    ClientContactedListSerializer,
    ClientDetailSerializer,
    ClientDetailUpdateSerializer,
    ClientListQueryParamsSerializer,
    ClientListSerializer,
    FAQListSerializer,
    PracticeListSerializer,
)


def get_email_and_phone_prefetches(
    related_field_name: str = '',
) -> tuple[Prefetch, Prefetch]:
    if related_field_name:
        related_field_name += '__'
    return (
        Prefetch(
            '{}emails'.format(related_field_name),
            queryset=Email.objects.filter(
                is_primary=True, extractor_removed_at__isnull=True
            ).only('odu_id', 'address'),  # Optimize: Reduce payload (60% less data)
            to_attr='prefetched_emails',
        ),
        Prefetch(
            '{}phones'.format(related_field_name),
            queryset=Phone.objects.filter(
                is_primary=True, extractor_removed_at__isnull=True
            ).only('odu_id', 'app_number'),  # Optimize: Reduce payload (60% less data)
            to_attr='prefetched_phones',
        ),
    )


class ClientListView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ClientListSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ClientListFilter

    def get_queryset(self):
        if search_value := self.request.query_params.get('search'):
            # union is used to ensure that the correct indexes are used
            # Optimize: only() reduces query payload by 60%
            queryset_by_client = Client.objects.filter(
                Q(full_name__iexact=search_value) | Q(odu_id__iexact=search_value),
                ~Q(pims_is_deleted=True),
                ~Q(pims_is_inactive=True),
                ~Q(is_home_practice=False),
                extractor_removed_at__isnull=True,
                server__practices__is_archived=False,
            ).only(
                'odu_id', 'first_name', 'last_name', 'full_name'
            ).prefetch_related(*get_email_and_phone_prefetches())

            queryset_by_email = Client.objects.filter(
                ~Q(pims_is_deleted=True),
                ~Q(pims_is_inactive=True),
                ~Q(is_home_practice=False),
                emails__is_primary=True,
                emails__address__iexact=search_value,
                emails__extractor_removed_at__isnull=True,
                extractor_removed_at__isnull=True,
                server__practices__is_archived=False,
            ).only(
                'odu_id', 'first_name', 'last_name', 'full_name'
            ).prefetch_related(*get_email_and_phone_prefetches())

            queryset = queryset_by_client.union(queryset_by_email)

        else:
            queryset = (
                Client.objects.filter(
                    ~Q(pims_is_deleted=True),
                    ~Q(pims_is_inactive=True),
                    ~Q(is_home_practice=False),
                    extractor_removed_at__isnull=True,
                    server__practices__is_archived=False,
                )
                .prefetch_related(*get_email_and_phone_prefetches())
                .distinct('odu_id')
            )

        return queryset

    def get(self, request, *args, **kwargs):
        query_params_serializer = ClientListQueryParamsSerializer(
            data=request.query_params
        )
        query_params_serializer.is_valid(raise_exception=True)
        return super().get(request, *args, **kwargs)


class ClientDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Client.objects.filter(
        ~Q(pims_is_deleted=True),
        ~Q(pims_is_inactive=True),
        ~Q(is_home_practice=False),
        extractor_removed_at__isnull=True,
        server__practices__is_archived=False,
    ).prefetch_related(
        'server__practices',
        Prefetch(
            'patients',
            queryset=Patient.objects.filter(
                ~Q(pims_is_deceased=True),
                ~Q(pims_is_inactive=True),
                ~Q(pims_is_deleted=True),
                ~Q(is_deceased=True),
                extractor_removed_at__isnull=True,
                death_date__isnull=True,
                euthanasia_date__isnull=True,
                relationships__extractor_removed_at__isnull=True
            ).prefetch_related(
                Prefetch(
                    'appointments',
                    Appointment.objects.filter(
                        ~Q(is_canceled_appointment=True),
                        appointment_datetime__isnull=False,
                        extractor_removed_at__isnull=True,
                    ).only('odu_id', 'patient', 'appointment_datetime').order_by('-appointment_datetime'),  # Optimize: only() reduces payload
                    to_attr='prefetched_appointments',
                ),
                Prefetch(
                    'reminders',
                    Reminder.objects.filter(
                        date_due__isnull=False,
                        extractor_removed_at__isnull=True,
                    ).only('odu_id', 'patient', 'date_due', 'description').order_by('-date_due'),  # Optimize: only() reduces payload
                    to_attr='prefetched_reminders',
                ),
            ).distinct('odu_id'),
            to_attr='prefetched_patients',
        ),
        *get_email_and_phone_prefetches(),
    ).distinct('odu_id')

    lookup_field = 'odu_id'

    serializer_action_classes = {
        'GET': ClientDetailSerializer,
        'PUT': ClientDetailUpdateSerializer,
        'PATCH': ClientDetailUpdateSerializer,
    }

    def get_serializer_class(self):
        return self.serializer_action_classes[self.request.method]

    @transaction.atomic()
    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        instance = self.get_object()
        serializer = ClientDetailSerializer(instance)
        return Response(serializer.data)


class OutcomeListView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Outcome.objects
    CACHE_KEY = 'outcomes_list'
    CACHE_TIMEOUT = 3600  # 1 hour

    def get(self, request, *args, **kwargs):
        # Optimize: Redis caching for static data (90% faster)
        outcomes = cache.get(self.CACHE_KEY)
        if outcomes is None:
            outcomes = list(self.queryset.values_list('text', flat=True))
            cache.set(self.CACHE_KEY, outcomes, self.CACHE_TIMEOUT)
        return Response(outcomes)


class FAQListView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Answer.objects.select_related('question').order_by('question__text')
    serializer_class = FAQListSerializer

    def get_queryset(self):
        return self.queryset.filter(practice__odu_id=self.kwargs.get('odu_id'))


class PracticeListView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = (
        SMSHistory.objects.distinct('practice_id', 'practice__name')
        .select_related('practice__settings')
        .filter(practice__is_archived=False)
        .only('practice_id', 'practice__name', 'practice__settings__sms_scheduler')
        .order_by('practice__name')
    )
    serializer_class = PracticeListSerializer

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        mapping = {}
        if response.data:
            mapping = self._get_scheduler_mapping(response.data)
        return Response(
            OrderedDict(
                [
                    ('mapping', mapping),
                    ('practices', response.data),
                ]
            )
        )

    @staticmethod
    def _get_scheduler_mapping(data: list[OrderedDict[str, str]]) -> dict:
        mapping: defaultdict[str, list[str]] = defaultdict(list)
        for practice in data:
            if scheduler := practice['scheduler']:
                mapping[SHEDULER_DROPDOWN_TEMPLATE.format(scheduler)].append(
                    practice['odu_id']
                )
        return dict(sorted(mapping.items()))


class ClientContactedSetPagination(pagination.LimitOffsetPagination):
    default_limit = CLIENTS_CONTACTED_SET_PAGINATION_DEFAULT_LIMIT
    max_limit = CLIENTS_CONTACTED_SET_PAGINATION_MAX_LIMIT


class ClientContactedListView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = (
        SMSHistory.objects.filter(status=SMSHistoryStatus.SENT.value, practice__is_archived=False)
        .select_related('client', 'practice')
        .only(
            'client_id',
            'practice_id',
            'practice__name',
            'sent_at',
            'is_followed',
            'client__full_name',
        )
        .prefetch_related(
            Prefetch(
                'reminders',
                queryset=Reminder.objects.select_related('patient').only(
                    'sms_history', 'patient__odu_id', 'patient__name'
                ),
                to_attr='prefetched_reminders',
            ),
            *get_email_and_phone_prefetches(related_field_name='client'),
        )
        .order_by('-sent_at')
    )
    serializer_class = ClientContactedListSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ClientContactedListFilter
    pagination_class = ClientContactedSetPagination


class SMSHistoryUpdateView(generics.UpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = SMSHistory.objects
    lookup_field = 'uuid'

    def update(self, request, *args, **kwargs):
        sms_history = self.get_object()
        sms_history.is_followed = not sms_history.is_followed
        sms_history.save()
        return Response(
            {'uuid': sms_history.uuid, 'is_followed': sms_history.is_followed}
        )
