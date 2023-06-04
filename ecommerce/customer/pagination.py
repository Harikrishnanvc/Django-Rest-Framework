from rest_framework.pagination import LimitOffsetPagination


class CustomerListPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 100

    def get_default_limit(self, request):
        limit = request.query_params.get('limit')
        if limit and limit.isdigit():
            return int(limit)
        return self.default_limit

    def get_max_limit(self, request):
        limit = request.query_params.get('max_limit')
        if limit and limit.isdigit():
            return min(int(limit), self.max_limit)
        return self.max_limit
