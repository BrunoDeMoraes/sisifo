from django.urls import path
from procurement import views as procurement_views

urlpatterns = [
    path('dashboard/', procurement_views.dashboard, name='dashboard'),
]