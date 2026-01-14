from django.urls import path

from apps.call_center.api.views import (
    ClientContactedListView,
    ClientDetailView,
    ClientListView,
    FAQListView,
    OutcomeListView,
    PracticeListView,
    SMSHistoryUpdateView,
)

urlpatterns = [
    path('clients/', ClientListView.as_view()),
    path('clients/<str:odu_id>', ClientDetailView.as_view()),
    path('clients/contacted/', ClientContactedListView.as_view()),
    path('practices/', PracticeListView.as_view()),
    path('outcomes/', OutcomeListView.as_view()),
    path('faq/<str:odu_id>', FAQListView.as_view()),
    path('sms/<uuid:uuid>/switch/', SMSHistoryUpdateView.as_view()),
]
