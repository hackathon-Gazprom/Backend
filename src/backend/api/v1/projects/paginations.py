from rest_framework.pagination import PageNumberPagination

from .constants import MEMBER_PAGE_SIZE


class MemberPagination(PageNumberPagination):
    page_size = MEMBER_PAGE_SIZE
