from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.loginView, name='login'),
    url(r'^register/$', views.registerView, name='register'),
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^board/(?P<board_id>[0-9]+)/$', views.board_utente, name='board_utente'),
    url(r'^burndown/(?P<board_id>[0-9]+)/$', views.burndown, name='burndown'),
]
