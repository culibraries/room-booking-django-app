from django.urls import path
from libcal.views import LibcalTokenView, SierraTokenView

urlpatterns = [
    path('libcal/token', LibcalTokenView.as_view(), name='libcal-token'),
    path('sierra/token', SierraTokenView.as_view(), name='sierra-token')
]
