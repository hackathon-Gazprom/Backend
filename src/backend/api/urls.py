from django.urls import include, path
from rest_framework_simplejwt.views import (
    token_obtain_pair,
    token_refresh,
    token_verify,
)

from .yasg import urlpatterns as doc_urls

auth_url = [
    path("", token_obtain_pair, name="token_obtain_pair"),
    path("refresh/", token_refresh, name="token_refresh"),
    path("verify/", token_verify, name="token_verify"),
]

urlpatterns = [
    path("v1/", include("api.v1.urls")),
    path("token/", include(auth_url)),
]


urlpatterns += doc_urls
