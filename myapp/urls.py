from django.urls import path
from . import views
from .views import (
    LandListingView, MyInterestsView,
    RegisterView, CustomLoginView, CustomLogoutView
)

urlpatterns = [
    # Home
    path('', views.index, name='index'),

    # Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('logout1/', views.logout1, name='logout1'),  # Only keep this if really needed

    # Admin
    path('admin/login/', views.admin_login, name='admin_login'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.manage_users, name='manage_users'),
    path('admin/manage-users/', views.manage_users, name='manage_users'),
    path('admin/reports/', views.generate_reports, name='generate_reports'),

    # Static/Informational Pages
    path('services/', views.services, name='services'),
    path('contact/', views.contact, name='contact'),
    path('faq/', views.faq, name='faq'),
    path('about/', views.about, name='about'),

    # User Dashboards
    path('landowner/dashboard/', views.landowner_dashboard, name='landowner_dashboard'),
    path('landseeker/dashboard/', views.landseeker_dashboard, name='landseeker_dashboard'),
    path('broker/dashboard/', views.broker_dashboard, name='broker_dashboard'),

    # Land Seeker Features
    path('land/search/', views.land_search, name='land_search'),
    path('my-interests/', MyInterestsView.as_view(), name='my_interests'),
    path('landseeker/profile/edit/', views.edit_landseeker_profile, name='edit_landseeker_profile'),
    path('landseeker_profile/', views.landseeker_profile, name='landseeker_profile'),

    # Land Owner Features
    path('landowner/lands/', views.view_my_lands, name='view_my_lands'),
    path('landowner/lands/add/', views.add_land, name='add_land'),
    path('landowner/lands/<int:land_id>/edit/', views.edit_land, name='edit_land'),
    path('landowner/lands/<int:land_id>/delete/', views.delete_land, name='delete_land'),

    # Listings
    path('land-details/<int:pk>/', views.land_details, name='land_details'),
    path('lands/', LandListingView.as_view(), name='land_list'),
    path('land-listings/', views.land_listing_list, name='land_listing_list'),
    path('manage-listings/', views.manage_listings, name='manage_listings'),
    path('add-land-listing/', views.add_land_listing, name='add_land_listing'),
    path('add_land_listing1/', views.add_land_listing1, name='add_land_listing1'),

    # Interests & Agreements
    path('express_interest/<int:land_id>/', views.express_interest, name='express_interest'),
    path('create_agreement/', views.create_agreement, name='create_agreement'),

    # Reports
    path('reports/', views.view_report, name='reports'),

    # Broker Facilitation
    path('land/<int:pk>/facilitate/', views.broker_facilitate_connection, name='broker_facilitate'),
]
