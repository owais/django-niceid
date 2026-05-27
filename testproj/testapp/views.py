from django.http import HttpResponse


def item_detail(request, item_id):
    return HttpResponse(str(item_id))
