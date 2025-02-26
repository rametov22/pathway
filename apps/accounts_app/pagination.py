from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


class Limit10Pagination(LimitOffsetPagination):
    default_limit = 10
    limit_query_param = "limit"
    max_limit = 100

    def get_paginated_response(self, data):
        return Response(
            {
                "offset": self.get_offset(self.request),
                "limit": self.get_limit(self.request),
                "previous": self.get_previous_link(),
                "next": self.get_next_link(),
                "count": self.count,
                "results": data,
            }
        )
