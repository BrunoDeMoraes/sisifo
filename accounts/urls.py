from django.urls import path
from accounts import views as accounts_views

urlpatterns = [
    path('login/', accounts_views.CustomLoginView.as_view(), name='login'),
    path('logout/', accounts_views.CustomLogoutView.as_view(), name='logout'),
]