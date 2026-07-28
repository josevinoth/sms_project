from django.urls import path
from .views import HistoryAPIView

urlpatterns = [
    path('api/history/', HistoryAPIView.as_view(), name='audit_history_api'),
]
