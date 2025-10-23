from rest_framework.pagination import PageNumberPagination


class PageLimitPagination(PageNumberPagination):
    """Пагинатор для страниц"""
    page_size = 6
    page_size_query_param = "limit"
