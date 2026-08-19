from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('upload/', views.upload_contract, name='upload'),
    path('login/', auth_views.LoginView.as_view(template_name='contracts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('chat/<int:contract_id>/', views.chat_with_contract, name='chat'),
]