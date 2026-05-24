from django.core.paginator import Paginator


def paginate(request, queryset, per_page):
    # Возвращает page_obj для queryset с постраничной пагинацией
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)
