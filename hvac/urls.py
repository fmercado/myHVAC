from django.urls import path

from . import views

# added for namespace isolation
app_name = 'hvac'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('<int:hvac_id>/command/', views.command, name='command'),
    path('<int:hvac_id>/plot/', views.plot, name='plot'),
]
