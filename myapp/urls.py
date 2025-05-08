from django.urls import path
from . import views
from .views import GeneratePDF
from .views import (
    LandListingView, MyInterestsView,
    RegisterView, CustomLoginView, CustomLogoutView,send_message, view_messages,
    create_agreement, accept_agreement,
    make_payment, generate_report, view_report,land_list
)

urlpatterns = [
    # Home
     path('', views.index, name='index'), 

    # Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
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

    # User Dashboards
    path('landowner/dashboard/', views.landowner_dashboard, name='landowner_dashboard'),
    path('landseeker/dashboard/', views.landseeker_dashboard, name='landseeker_dashboard'),
    path('broker/dashboard/', views.broker_dashboard, name='broker_dashboard'),


    # Land Seeker Features
    path('land/search/', views.land_search, name='land_search'),
    path('interest-details/<int:interest_id>/', views.view_interest_details, name='view_interest_details'),

    path('my-interests/', MyInterestsView.as_view(), name='my_interests'),
    path('withdraw-interest/<int:interest_id>/', views.withdraw_interest, name='withdraw_interest'),

    path('landowner/profile/', views.landowner_profile, name='landowner_profile'),
    path('edit-profile/', views.edit_landowner_profile, name='edit_landowner_profile'),
    path('landseeker/profile/edit/', views.edit_landseeker_profile, name='edit_landseeker_profile'),
    path('landseeker_profile/', views.landseeker_profile, name='landseeker_profile'),

    # Land Owner Features
    path('landowner/lands/', views.view_my_lands, name='view_my_lands'),
    path('landowner/lands/add/', views.add_land, name='add_land'),
    path('newland/', views.newland_view, name='newland'),
        path('agreements/', views.agreements_view, name='agreements'),

    path('lands/<int:pk>/', views.land_details, name='land_details'),

    path('lands/', views.view_lands, name='view_lands'),  # For all lands
    path('lands/<int:landowner_id>/', views.view_lands, name='view_lands_by_owner'),  # For specific landowner's lands

    path('mylands/', views.mylands_view, name='mylands'),
    path('landowners/', views.landowners_list, name='landowners_list'),
    path('landseekers/', views.landseekers_list, name='landseekers_list'),
    path('landseeker/<int:seeker_id>/', views.view_landseeker_profile, name='view_landseeker_profile'),
    


    path('landowner/<int:pk>/', views.landowner_detail, name='landowner_detail'),
    path('verify-landowners/', views.verify_landowners, name='verify_landowners'),
    path('landowners/<int:user_id>/approve/', views.approve_landowner, name='approve_landowner'),
    path('landowners/<int:user_id>/reject/', views.reject_landowner, name='reject_landowner'),
    path('mark-notification-read/<int:notification_id>/', views.mark_notification_as_read, name='mark_notification_as_read'),
    path('message/send/<int:user_id>/', views.send_message, name='send_message'),
    path('inbox/', views.inbox, name='inbox'),






    path('landowner/lands/<int:land_id>/edit/', views.edit_land, name='edit_land'),
    path('landowner/lands/<int:land_id>/delete/', views.delete_land, name='delete_land'),

    # Listings
    path('land-details/<int:pk>/', views.land_details, name='land_details'),  # Detail view for a specific land
    path('lands/', views.LandListingView.as_view(), name='land_list'),          # List view (use class-based view)
    path('manage-listings/', views.manage_listings, name='manage_listings'),    # Landowner manage listings
    path('add-land-listing/', views.add_land_listing, name='add_land_listing'), # Add new land
    path('add-land-listing1/', views.add_land_listing1, name='add_land_listing1'), 
    path('lands/', views.view_my_lands, name='landseeker_view'),
    path('generate-pdf/', GeneratePDF.as_view(), name='generate_pdf'),

    # Interests & Agreements
    path('approve-interest/<int:interest_id>/', views.approve_interest, name='approve_interest'),

    path('express_interest/<int:land_id>/', views.express_interest, name='express_interest'),
    path('create_agreement/', views.create_agreement, name='create_agreement'),

    # Reports
     path('reports/', views.view_report, name='reports'),
     path('report/generate/<int:agreement_id>/', generate_report, name='generate_report'),
    # Broker Facilitation
    path('land/<int:pk>/facilitate/', views.broker_facilitate_connection, name='broker_facilitate'),
    
     # ---------- Messaging ----------

path('message/send/<int:landowner_id>/', send_message, name='send_message'),    
path('messages/', view_messages, name='view_messages'),
path('payment1/', views.payment1, name='payment1'),
    
    # ---------- Payments ----------
    path('payment/make/<int:agreement_id>/', make_payment, name='make_payment'),

    
]
