from django.urls import path
from . import views

urlpatterns = [
    path('',views.index, name='index'),
    path('<int:chef_id>/', views.detail, name='detail'),
]