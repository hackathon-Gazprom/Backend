from django.core.cache import cache
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, views
from rest_framework.response import Response

from apps.projects.models import Department
from apps.users.models import Profile
from .serializers import FilterSerializer


class FilterViewSet(views.APIView):
    permission_classes = [permissions.AllowAny]
    swagger_tags = ["filter"]

    def get_cached_values(
        self, cache_key, *, lookup_field, model, exclude=None
    ):
        res = cache.get(cache_key)
        if res is None:
            qs = model.objects
            if exclude is not None:
                ex = Q()
                for k, v in exclude.items():
                    ex |= Q(**{k: v})
                qs = qs.exclude(ex)
            res = set(qs.values_list(lookup_field, flat=True))
            cache.set(cache_key, res)
        return sorted(res)

    @swagger_auto_schema(responses={200: FilterSerializer()})
    def get(self, request, format=None):
        cities = self.get_cached_values(
            "cities",
            lookup_field="city",
            model=Profile,
            exclude={"city": ""},
        )
        positions = self.get_cached_values(
            "positions",
            lookup_field="position",
            model=Profile,
            exclude={"position__isnull": True, "position": ""},
        )
        departments = self.get_cached_values(
            "departments",
            lookup_field="name",
            model=Department,
        )
        data = {
            "cities": cities,
            "positions": positions,
            "departments": departments,
        }
        serializer = FilterSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)
