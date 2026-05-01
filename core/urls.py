from django.urls import path
from . import views

urlpatterns = [
    # ── Existing Public ────────────────────────────────────────────
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.student_login, name='login'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('logout/', views.student_logout, name='logout'),

    # ── Existing Student ───────────────────────────────────────────
    path('dashboard/', views.dashboard, name='dashboard'),
    path('apply/', views.apply, name='apply'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('download-pdf/<int:app_id>/', views.download_pdf, name='download_pdf'),

    # ── Feature 1: Profile Edit ─────────────────────────────────────
    path('profile/', views.profile_edit, name='profile_edit'),

    # ── Existing Admin ─────────────────────────────────────────────
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-applications/', views.admin_applications, name='admin_applications'),
    path('admin-applications/<int:app_id>/', views.admin_application_detail, name='admin_application_detail'),

    # ── Feature 2: CSV Export ───────────────────────────────────────
    path('admin-export-csv/', views.export_csv, name='export_csv'),

    # ── Features 5 & 6: Merit List (course filter) + Merit PDF ─────
    path('merit-list/', views.merit_list, name='merit_list'),
    path('download-merit-pdf/', views.download_merit_pdf, name='download_merit_pdf'),

    # ── Feature 8: Course Management ───────────────────────────────
    path('admin-courses/', views.admin_courses, name='admin_courses'),
    path('admin-courses/add/', views.admin_course_add, name='admin_course_add'),
    path('admin-courses/<int:course_id>/edit/', views.admin_course_edit, name='admin_course_edit'),
    path('admin-courses/<int:course_id>/toggle/', views.admin_course_toggle, name='admin_course_toggle'),

    # ── Payment Gateway ─────────────────────────────────────────────
    path('payment/initiate/', views.initiate_payment, name='initiate_payment'),
    path('payment/verify/', views.verify_payment, name='verify_payment'),
    path('payment/confirmation/', views.payment_confirmation, name='payment_confirmation'),
    path('payment/failed/', views.payment_failed, name='payment_failed'),
    path('payment/acknowledgment/pdf/', views.generate_acknowledgment_pdf, name='acknowledgment_pdf'),

    # ── Feature: Forgot / Reset Password ───────────────────────────────────
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.reset_password, name='reset_password'),
]
