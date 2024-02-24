from django.urls import path
from . import views
from django.contrib.auth import views as auth_views #import this
urlpatterns = [
    path('login_page', views.login_page,name='login_page'),#Login_page
    path('logout_page', views.logout_page,name='logout_page'),#Logout_page
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name="password/password_reset_done.html"), name='password_reset_done'),  # Password Reset
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="password/password_reset_confirm.html"), name='password_reset_confirm'),# Password Reset
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password/password_reset_complete.html'), name='password_reset_complete'),# Password Reset
    path('home_page', views.home_page, name='home_page'),  # Home_page
    path('user_add', views.user_add, name='user_add'),  # Registration_page add
    path('user_update/<int:user_id>/', views.user_add, name='user_update'),  # Update user
    path('user_list', views.user_list, name='user_list'),  # user_list
    path('user_delete/<int:user_id>/', views.user_delete, name='user_delete'),  # Delete user
    path('password_reset', views.password_reset_request, name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name="password/password_reset_done.html"), name='password_reset_done'),  # Password Reset
    path('query_add', views.query_add, name='query_add'),  # Registration_page add
    path('query_update/<int:query_id>/', views.query_add, name='query_update'),  # Update query
    path('query_list', views.query_list, name='query_list'),  # query_list
    path('query_delete/<int:query_id>/', views.query_delete, name='query_delete'),  # Delete query
]

