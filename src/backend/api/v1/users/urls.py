from django.urls import path, include
from rest_framework import routers

from api.v1.users import views

router = routers.DefaultRouter()
router.register("users", views.UserUpdateView)

urlpatterns = [
    path("", include(router.urls)),
]
