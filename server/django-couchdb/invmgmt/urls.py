from django.urls import path

from . import views

urlpatterns = [
    path("reagents/", views.reagents, name="reagents"),
    path("lots/", views.lots, name="lots"),
    path("container_types/", views.container_type, name="container_types"),
    path("container_by_barcode", views.container_by_barcode, name="container_by_barcode"),
    path("container", views.add_container, name="container"),
    path("container/<str:id>", views.container, name="container_by_id"),
    path("locate_container", views.locate_container, name="locate_container"),
    path("pick_list", views.pick_list, name="pick_list"),
    #
    path("login", views.app_login, name="login"),
]

