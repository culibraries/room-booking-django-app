from django.urls import path
from .views import LibcalTokenView, SierraSearchView

urlpatterns = [
    path('libcal/token', LibcalTokenView.as_view(), name='libcal-token'),
    path('sierra/search', SierraSearchView.as_view(), name='sierra-search')
]
