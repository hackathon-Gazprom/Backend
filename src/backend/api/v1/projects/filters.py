from django_filters.rest_framework import CharFilter, FilterSet

from apps.projects.models import Member


class MemberFilter(FilterSet):
    position = CharFilter(
        field_name="user__profile__position",
        lookup_expr="iexact",
    )
    city = CharFilter(
        field_name="user__profile__city",
        lookup_expr="iexact",
    )

    class Meta:
        model = Member
        fields = ("department", "position", "city")
