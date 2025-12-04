"""URL configuration for the API app."""
from django.urls import path

from .views import NumberToEnglishView

app_name = "api"

urlpatterns = [
    path("num_to_english", NumberToEnglishView.as_view(), name="num_to_english"),
]
