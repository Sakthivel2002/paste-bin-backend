from django.urls import path
from .views import healthz, create_paste, fetch_paste, view_paste_html

urlpatterns = [
    path('api/healthz', healthz),
    path('api/pastes', create_paste),
    path('api/pastes/<str:id>', fetch_paste),
    path('p/<str:id>', view_paste_html),
]
