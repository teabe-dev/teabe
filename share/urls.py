from share import views
from django.urls import include, path, re_path

urlpatterns = [
    re_path(r'group/$', views.Group.as_view()),
]
