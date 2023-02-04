from django.urls import include, path, re_path

from share import views

urlpatterns = [
    path(r'', views.Share.as_view()),
    re_path(r'group/(\S+)/$', views.Group.as_view()),
    re_path(r'group_create/', views.GroupCreate.as_view()),
    re_path(r'information/', views.Information.as_view()),

    re_path(r'modal_group_members/(\S+)/$', views.ModalGroupMembers.as_view()),
]
