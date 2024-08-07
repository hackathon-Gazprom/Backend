from django_filters.rest_framework import FilterSet, CharFilter

from apps.projects.models import Member


class MemberFilter(FilterSet):
    position = CharFilter(
        field_name="user__profile__position",
        lookup_expr="iexact",
        # source="user__profile__position",
    )
    city = CharFilter(
        field_name="user__profile__city",
        lookup_expr="iexact",
        # source="user__profile__city",
    )

    class Meta:
        model = Member
        fields = ("department", "position", "city")
