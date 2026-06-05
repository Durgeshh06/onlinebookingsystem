from django.urls import path
from . import views

urlpatterns = [
    # Customer Pages
    path('', views.home, name='home'),
    path('services/', views.catalog, name='catalog'),
    path('services/<slug:slug>/', views.detail, name='detail'),
    path('book/<slug:slug>/', views.book, name='book'),
    path('profile/', views.profile, name='profile'),
    path('booking/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),

    # Administrative Dashboard & Actions
    path('dashboard/admin-metrics/', views.admin_metrics, name='admin_metrics'),
    path('dashboard/assign-pandit/<int:booking_id>/', views.assign_pandit, name='assign_pandit'),

    # Authentication Pages
    path('accounts/login/', views.login_user, name='login'),
    path('accounts/register/', views.register_user, name='register'),
    path('accounts/logout/', views.logout_user, name='logout'),
]
