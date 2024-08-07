from rest_framework.pagination import PageNumberPagination

from .constants import PROJECT_PAGE_SIZE


class ProjectsPagination(PageNumberPagination):
    page_size = PROJECT_PAGE_SIZE
    page_size_query_param = "limit"
