from django.urls import include, path

urlpatterns = [
    path("", include("api.v1.general.urls")),
    path("", include("api.v1.projects.urls")),
    path("", include("api.v1.users.urls")),
]
