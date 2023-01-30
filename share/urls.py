from share import views
from django.urls import include, path, re_path

urlpatterns = [
    path(r'', views.Share.as_view()),
    re_path(r'new_group/', views.NewGroup.as_view()),
    
    # re_path(r'group/(\S+)/$', views.GroupJoin.as_view()),
]
