from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.loginView, name='login'),
    url(r'^logout/$', views.logoutView, name='logout'),
    url(r'^register/$', views.registerView, name='register'),
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^add_board/$', views.addBoard, name='add_board'),
    url(r'^add_column/$', views.addColumn, name='add_column'),
    url(r'^add_card/(?P<board_id>[0-9]+)/$', views.addCard, name='add_card'),
    url(r'^add_user/(?P<board_id>[0-9]+)/$', views.addUser, name='add_user'),
    url(r'^edit_column/(?P<col_id>[0-9]+)/$', views.editColumn, name='edit_column'),
    url(r'^edit_card/(?P<card_id>[0-9]+)/$', views.editCard, name='edit_card'),
    url(r'^board/(?P<board_id>[0-9]+)/$', views.board_details, name='board_details'),
    url(r'^burndown/(?P<board_id>[0-9]+)/$', views.burndown, name='burndown'),
]
