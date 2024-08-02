from django.urls import include, path
from rest_framework import routers

from api.v1.users import views

router = routers.DefaultRouter()
router.register("users", views.UserViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
