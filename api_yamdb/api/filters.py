from django_filters import rest_framework, utils


class IsOwnerFilterBackend(rest_framework.DjangoFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if request.query_params.get("genre"):
            queryset = queryset.filter(
                genre__slug=request.query_params["genre"]
            )
            return queryset
        if request.query_params.get("category"):
            queryset = queryset.filter(
                category__slug=request.query_params["category"]
            )
            return queryset
        filterset = self.get_filterset(request, queryset, view)
        if filterset is None:
            return queryset
        if not filterset.is_valid() and self.raise_exception:
            raise utils.translate_validation(filterset.errors)
        return filterset.qs
