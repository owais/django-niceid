from django.urls import path

from testproj.testapp import views

urlpatterns = [
    path("items/<niceid:item_id>/", views.item_detail, name="item-detail"),
]
