from django.urls import include, path, re_path

from share import views

urlpatterns = [
    path(r'', views.Share.as_view()),
    re_path(r'group/(\S+)/$', views.Group.as_view()),
    re_path(r'group_create/', views.GroupCreate.as_view()),
    re_path(r'information/', views.Information.as_view()),

    re_path(r'modal_group_members/(\S+)/$', views.ModalGroupMembers.as_view()),
    re_path(r'modal_group_join/(\S+)/$', views.ModalGroupJoin.as_view()),
    re_path(r'modal_group_admin/(\S+)/$', views.ModalGroupAdmin.as_view()),
    re_path(r'modal_group_add_item/(\S+)/(\S+)/$', views.ModalGroupAddItam.as_view()),
    re_path(r'modal_group_send_price/(\S+)/(\S+)/$', views.ModalGroupSendPrice.as_view()),
    re_path(r'modal_group_sort_share/(\S+)/$', views.ModalGroupSortShare.as_view()),

    re_path(r'modal_add_item/(\S+)/$', views.ModalAddItam.as_view()),
]


