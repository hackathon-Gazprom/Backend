from django.urls import path

from . import views

urlpatterns = [
    path("filters/", views.FilterViewSet.as_view(), name="filters"),
]
