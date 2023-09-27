from django.urls import path
from .views import LibcalTokenView, SierraSearchView, FolioSearchView

urlpatterns = [
    path('libcal/token', LibcalTokenView.as_view(), name='libcal-token'),
    path('sierra/search', SierraSearchView.as_view(), name='sierra-search'),
    path('folio/search', FolioSearchView.as_view(), name='folio-search')
]
