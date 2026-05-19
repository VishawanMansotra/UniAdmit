import io
import csv
import json
import hmac
import hashlib
import threading
import pyotp
from datetime import date
from django.db import IntegrityError

import razorpay
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.db.models import Q, F
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.decorators.csrf import csrf_exempt

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image
)

from .models import StudentProfile, Application, Course, Payment, AdmissionRound, MeritListPDF
from .forms import StudentRegistrationForm, ProfileEditForm, ApplicationForm, CourseForm, AdmissionRoundForm, MeritListPDFForm


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _get_courses_dict():
    """Returns {code: name} dict from Course model, with fallback."""
    try:
        d = {c.code: c.name for c in Course.objects.all()}
        if d:
            return d
    except Exception:
        pass
    return {
        'CSE': 'B.Tech Computer Science Engineering',
        'CIVIL': 'B.Tech Civil Engineering',
    }


def _send_email(subject, body, recipient_email):
    """
    Feature: Email Notifications
    Sends a plain-text email in a background thread via Django's send_mail.
    Running in a thread ensures the web request completes immediately,
    preventing timeouts on live hosts (e.g. Railway) when SMTP is slow.
    """
    def _send():
        try:
            send_mail(
                subject=f'UniAdmit — UIET Jammu | {subject}',
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient_email],
                fail_silently=False,
            )
        except Exception:
            # Silently ignore — email failure must not break any user flow
            pass

    threading.Thread(target=_send, daemon=True).start()


# ─── Public Views ────────────────────────────────────────────────────────────

def home(request):
    published_results = MeritListPDF.objects.filter(is_published=True)
    return render(request, 'home.html', {
        'published_results': published_results
    })


def register(request):
    """
    Feature OTP: Registration with email OTP verification.
    Step 1 — Collect form data, validate email domain, create INACTIVE user,
    send OTP to email, redirect to OTP verification page.
    """
    form = StudentRegistrationForm()
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            if form.cleaned_data['password'] != form.cleaned_data['confirm_password']:
                messages.error(request, 'Passwords do not match!')
                return render(request, 'register.html', {'form': form})
            if User.objects.filter(email=form.cleaned_data['email']).exists():
                messages.error(request, 'Email already registered!')
                return render(request, 'register.html', {'form': form})

            # Store all form data in session
            pending = {
                'first_name': form.cleaned_data['first_name'],
                'middle_name': form.cleaned_data.get('middle_name', ''),
                'last_name': form.cleaned_data['last_name'],
                'email': form.cleaned_data['email'],
                'password': form.cleaned_data['password'],
                'phone': form.cleaned_data['phone'],
                'gender': form.cleaned_data['gender'],
                'date_of_birth': str(form.cleaned_data['date_of_birth']),
                'address': form.cleaned_data['address'],
            }

            request.session['pending_registration'] = pending

            # Generate TOTP secret and OTP
            secret = pyotp.random_base32()
            request.session['otp_secret'] = secret
            otp = pyotp.TOTP(secret, interval=300).now()  # valid 5 min

            _send_email(
                subject='Your OTP for UniAdmit Registration',
                body=(
                    f"Dear {pending['first_name']},\n\n"
                    "Thank you for registering at UniAdmit — UIET, University of Jammu.\n\n"
                    f"  Your One-Time Password (OTP) : {otp}\n\n"
                    "This OTP is valid for 5 minutes. Do not share it with anyone.\n\n"
                    "If you did not request this, please ignore this email.\n\n"
                    "Regards,\n"
                    "Admissions Office\n"
                    "UIET, University of Jammu"
                ),
                recipient_email=pending['email'],
            )
            messages.info(request, f"An OTP has been sent to {pending['email']}. Please enter it below.")
            return redirect('verify_otp')
    return render(request, 'register.html', {'form': form})


def verify_otp(request):
    """
    Feature OTP: Step 2 — Verify the OTP entered by the student.
    On success, create the user as active, send welcome email, log them in.
    """
    pending = request.session.get('pending_registration')
    otp_secret = request.session.get('otp_secret')

    if not pending or not otp_secret:
        messages.error(request, 'Session expired. Please register again.')
        return redirect('register')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp', '').strip()

        totp = pyotp.TOTP(otp_secret, interval=300)
        if totp.verify(entered_otp, valid_window=1):
            # OTP valid — create the user now (active)

            # Guard: if a user with this email already exists, don't crash
            if User.objects.filter(email=pending['email']).exists():
                del request.session['pending_registration']
                del request.session['otp_secret']
                messages.error(
                    request,
                    'An account with this email already exists. Please log in instead.'
                )
                return redirect('login')

            try:
                user = User.objects.create_user(
                    username=pending['email'],
                    email=pending['email'],
                    password=pending['password'],
                    first_name=pending['first_name'],
                    last_name=pending['last_name'],
                    is_active=True,
                )
            except IntegrityError:
                del request.session['pending_registration']
                del request.session['otp_secret']
                messages.error(
                    request,
                    'An account with this email already exists. Please log in instead.'
                )
                return redirect('login')
            profile_kwargs = {
                'user': user,
                'middle_name': pending.get('middle_name', ''),
                'phone': pending['phone'],
                'gender': pending['gender'],
                'date_of_birth': pending['date_of_birth'],
                'address': pending['address'],
            }
            profile = StudentProfile.objects.create(**profile_kwargs)

            # Clear session data
            del request.session['pending_registration']
            del request.session['otp_secret']

            # Send welcome email
            _send_email(
                subject='Welcome to UniAdmit',
                body=(
                    f"Dear {user.get_full_name()},\n\n"
                    "Welcome to the University Admission Portal — UIET, University of Jammu.\n\n"
                    "Your email has been verified and your account is now active.\n"
                    f"  Registered Email : {user.email}\n\n"
                    "You can now log in and submit your B.Tech admission application.\n"
                    "  Portal: http://127.0.0.1:8000/login/\n\n"
                    "Regards,\n"
                    "Admissions Office\n"
                    "UIET, University of Jammu"
                ),
                recipient_email=user.email,
            )
            login(request, user)
            messages.success(request, f'Email verified! Welcome, {user.first_name}. You are now logged in.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid or expired OTP. Please try again.')
            return render(request, 'verify_otp.html', {'email': pending['email']})

    return render(request, 'verify_otp.html', {'email': pending.get('email', '')})


def student_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            if user.is_staff:
                messages.error(request, 'Please use Admin Login page!')
                return render(request, 'login.html')
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid email or password!')
    return render(request, 'login.html')


def student_logout(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('login')


def admin_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        # Look up the user by email first, then verify the password directly.
        # This handles the case where the superuser's username differs from
        # their email (e.g. username='admin', email='admin@uiet.ac.in').
        # Using .filter(email=email).first() to avoid MultipleObjectsReturned
        # if there are duplicate admin emails in the database.
        user = User.objects.filter(email=email).first()
        if user is not None and user.is_staff and user.check_password(password):
            login(request, user)
            messages.success(request, f'Welcome, Admin {user.first_name}!')
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid admin credentials!')
    return render(request, 'admin_login.html')


# ─── Student Views ────────────────────────────────────────────────────────────

@login_required(login_url='/login/')
def dashboard(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    try:
        student = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        messages.error(request, 'Profile not found. Please register again.')
        return redirect('home')
    applications = Application.objects.filter(student=request.user)
    applications_count = applications.count()
    return render(request, 'dashboard.html', {
        'student': student,
        'applications_count': applications_count,
        'applications': applications,
        'courses_dict': _get_courses_dict(),
    })


@login_required(login_url='/login/')
def profile_edit(request):
    """Feature 1: Edit student profile."""
    if request.user.is_staff:
        return redirect('admin_dashboard')
    try:
        profile = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        messages.error(request, 'Profile not found.')
        return redirect('home')

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES)
        if form.is_valid():
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.save()
            profile.middle_name = form.cleaned_data.get('middle_name', '')
            profile.phone = form.cleaned_data['phone']
            profile.date_of_birth = form.cleaned_data['date_of_birth']
            profile.address = form.cleaned_data['address']
            profile.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('dashboard')
    else:
        form = ProfileEditForm(initial={
            'first_name': request.user.first_name,
            'middle_name': profile.middle_name,
            'last_name': request.user.last_name,
            'phone': profile.phone,
            'date_of_birth': profile.date_of_birth,
            'address': profile.address,
        })
    return render(request, 'profile_edit.html', {'form': form, 'student': profile})


@login_required(login_url='/login/')
def apply(request):
    """
    Round-aware application view.
    Reads AdmissionRound to determine what's open, blocks if closed,
    and passes round info to form and template.
    """
    courses_dict = _get_courses_dict()
    current_round = AdmissionRound.get_active()

    # If round is closed, show a closed message instead of the form
    if current_round == 'closed':
        return render(request, 'apply.html', {
            'round_closed': True,
            'courses_dict': courses_dict,
        })

    # Round labels for display
    round_labels = {
        'round1_jee':   'Round 1 — JEE Mains 2026',
        'round2_cuet':  'Round 2 — CUET UG',
        'round3_board': 'Round 3 — 10+2 Board Score',
    }
    round_label = round_labels.get(current_round, current_round)

    # Check for any existing application by this student
    existing = Application.objects.filter(student=request.user).first()
    if existing:
        return render(request, 'apply.html', {
            'duplicate': True,
            'existing_app': existing,
            'courses_dict': courses_dict,
            'current_round': current_round,
            'round_label': round_label,
        })

    try:
        profile = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        profile = None

    initial_data = {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
    }
    if profile:
        initial_data.update({
            'phone': profile.phone,
            'gender': profile.gender,
            'date_of_birth': profile.date_of_birth,
            'correspondence_address': profile.address,
        })

    form = ApplicationForm(initial=initial_data, current_round=current_round)
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES, current_round=current_round)
        if form.is_valid():
            selected_pref1 = form.cleaned_data['preference1']

            # Duplicate guard
            if Application.objects.filter(
                student=request.user,
                preference1=selected_pref1,
            ).exists():
                return render(request, 'apply.html', {
                    'duplicate': True,
                    'courses_dict': courses_dict,
                    'current_round': current_round,
                    'round_label': round_label,
                })

            try:
                app = Application.objects.create(
                    student=request.user,
                    applied_round=current_round,
                    first_name=form.cleaned_data['first_name'],
                    middle_name=form.cleaned_data.get('middle_name'),
                    last_name=form.cleaned_data['last_name'],
                    preference1=selected_pref1,
                    preference2=form.cleaned_data['preference2'],
                    preference3=form.cleaned_data.get('preference3'),
                    jee_score=form.cleaned_data.get('jee_score'),
                    cuet_score=form.cleaned_data.get('cuet_score'),
                    board_percentage=form.cleaned_data.get('board_percentage'),
                    father_name=form.cleaned_data['father_name'],
                    mother_name=form.cleaned_data['mother_name'],
                    gender=form.cleaned_data['gender'],
                    date_of_birth=form.cleaned_data['date_of_birth'],
                    category=form.cleaned_data['category'],
                    phone=form.cleaned_data['phone'],
                    correspondence_address=form.cleaned_data['correspondence_address'],
                    permanent_address=form.cleaned_data['permanent_address'],
                    is_jk_resident=form.cleaned_data['is_jk_resident'],
                    physics_marks=form.cleaned_data['physics_marks'],
                    chemistry_marks=form.cleaned_data['chemistry_marks'],
                    math_marks=form.cleaned_data['math_marks'],
                    max_marks=form.cleaned_data['max_marks'],
                    board_name=form.cleaned_data['board_name'],
                    school_name=form.cleaned_data['school_name'],
                    # Personal documents
                    passport_photo=form.cleaned_data.get('passport_photo'),
                    marksheet_10th=form.cleaned_data['marksheet_10th'],
                    marksheet_12th=form.cleaned_data['marksheet_12th'],
                    aadhar_card=form.cleaned_data.get('aadhar_card'),
                    character_certificate=form.cleaned_data.get('character_certificate'),
                    category_certificate=form.cleaned_data.get('category_certificate'),
                    domicile_certificate=form.cleaned_data.get('domicile_certificate'),
                    migration_certificate=form.cleaned_data.get('migration_certificate'),
                    signature=form.cleaned_data['signature'],
                    # Score verification
                    entrance_scorecard=form.cleaned_data.get('entrance_scorecard'),
                )
            except IntegrityError:
                return render(request, 'apply.html', {
                    'duplicate': True,
                    'courses_dict': courses_dict,
                    'current_round': current_round,
                    'round_label': round_label,
                })

            # Confirmation email
            course_name = courses_dict.get(app.preference1, app.preference1)
            _send_email(
                subject='Application Received',
                body=(
                    f"Dear {request.user.get_full_name()},\n\n"
                    "Thank you for applying. Your application has been successfully submitted.\n\n"
                    f"  Application ID  : {app.id}\n"
                    f"  Round           : {round_label}\n"
                    f"  Program Applied : {course_name}\n"
                    f"  Submitted On    : {app.applied_at.strftime('%d %B %Y')}\n"
                    f"  Current Status  : Pending Review\n\n"
                    "You will receive another email once your application is reviewed by the admissions team.\n"
                    "Regards,\n"
                    "Admissions Office\n"
                    "UIET, University of Jammu"
                ),
                recipient_email=request.user.email,
            )
            messages.success(request, 'Application submitted successfully!')
            return redirect('my_applications')

    return render(request, 'apply.html', {
        'form': form,
        'courses_dict': courses_dict,
        'current_round': current_round,
        'round_label': round_label,
    })


@login_required(login_url='/login/')
def my_applications(request):
    applications = Application.objects.filter(student=request.user)
    return render(request, 'my_applications.html', {
        'applications': applications,
        'courses_dict': _get_courses_dict(),
    })


# ─── Admin Views ──────────────────────────────────────────────────────────────

@staff_member_required(login_url='/login/')
def admin_dashboard(request):
    total = Application.objects.count()
    round1 = Application.objects.filter(applied_round='round1_jee').count()
    round2 = Application.objects.filter(applied_round='round2_cuet').count()
    round3 = Application.objects.filter(applied_round='round3_board').count()
    recent_applications = Application.objects.all().order_by('-applied_at')[:5]

    # Feature 7: Build chart data dynamically from Course model
    courses_dict = _get_courses_dict()
    course_labels = list(courses_dict.keys())
    course_data_vals = [
        Application.objects.filter(preference1=code).count()
        for code in course_labels
    ]
    default_bar_colors = [
        '#1565c0', '#1b5e20', '#e65100', '#6a1b9a', '#00838f', '#c62828',
    ]
    course_bar_colors = default_bar_colors[:len(course_labels)]

    return render(request, 'admin_dashboard.html', {
        'total': total,
        'round1': round1,
        'round2': round2,
        'round3': round3,
        'recent_applications': recent_applications,
        # Round doughnut chart data
        'chart_round_labels': json.dumps(['Round 1 (JEE)', 'Round 2 (CUET)', 'Round 3 (Board)']),
        'chart_round_data': json.dumps([round1, round2, round3]),
        'chart_round_colors': json.dumps(['#0d6efd', '#198754', '#fd7e14']),
        # Course bar chart data
        'chart_course_labels': json.dumps(list(courses_dict.values())),
        'chart_course_data': json.dumps(course_data_vals),
        'chart_course_colors': json.dumps(course_bar_colors),
    })


@staff_member_required(login_url='/login/')
def admin_applications(request):
    """Feature 4: Search added."""
    search_query = request.GET.get('q', '').strip()

    applications = Application.objects.all().order_by('-applied_at')

    if search_query:
        applications = applications.filter(
            Q(student__first_name__icontains=search_query) |
            Q(student__last_name__icontains=search_query) |
            Q(student__email__icontains=search_query)
        )

    return render(request, 'admin_applications.html', {
        'applications': applications,
        'search_query': search_query,
    })


@staff_member_required(login_url='/login/')
def admin_application_detail(request, app_id):
    application = Application.objects.get(id=app_id)
    return render(request, 'admin_application_detail.html', {
        'application': application,
        'courses_dict': _get_courses_dict(),
    })


# ─── Feature: Forgot / Reset Password ────────────────────────────────────────

def forgot_password(request):
    """
    Step 1: Student enters their email. We generate a signed UID+token link
    and email it. Uses Django's built-in PasswordResetTokenGenerator.
    """
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email.')
            return render(request, 'forgot_password.html')

        # Build the reset link using Django's token generator
        token_generator = PasswordResetTokenGenerator()
        uid = urlsafe_base64_encode(force_bytes(user.pk))   # URL-safe user id
        token = token_generator.make_token(user)            # signed, time-limited token
        reset_link = f'http://127.0.0.1:8000/reset-password/{uid}/{token}/'

        _send_email(
            subject='Password Reset Request',
            body=(
                f"Dear {user.get_full_name() or user.email},\n\n"
                "We received a request to reset the password for your UniAdmit account.\n\n"
                "Click the link below to set a new password (expires in 24 hours):\n"
                f"  {reset_link}\n\n"
                "If you did not request a password reset, please ignore this email. "
                "Your account remains secure.\n\n"
                "Regards,\n"
                "Admissions Office\n"
                "UIET, University of Jammu"
            ),
            recipient_email=user.email,
        )
        # Show success regardless (prevents email enumeration)
        messages.success(
            request,
            'A password reset link has been sent to your email address.'
        )
        return redirect('forgot_password')

    return render(request, 'forgot_password.html')


def reset_password(request, uidb64, token):
    """
    Step 2: Student clicks the link from the email.
    We validate the UID + token, then let them set a new password.
    The token is invalidated after use because Django's token generator
    factors in the user's last_login and password hash.
    """
    token_generator = PasswordResetTokenGenerator()

    # Decode the user ID from the URL
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    # Validate the token against the user
    if user is None or not token_generator.check_token(user, token):
        messages.error(request, 'This reset link is invalid or has expired.')
        return render(request, 'reset_password.html', {'invalid_link': True})

    if request.method == 'POST':
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
            return render(request, 'reset_password.html', {
                'uidb64': uidb64, 'token': token
            })
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'reset_password.html', {
                'uidb64': uidb64, 'token': token
            })

        # Set new password — this also invalidates the token (password hash changes)
        user.set_password(new_password)
        user.save()

        messages.success(request, 'Password reset successful. Please log in.')
        return redirect('login')

    return render(request, 'reset_password.html', {'uidb64': uidb64, 'token': token})


@staff_member_required(login_url='/login/')
def export_csv(request):
    """Feature 2: Export applications as CSV."""
    applications = Application.objects.all().order_by('-applied_at')

    courses_dict = _get_courses_dict()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = (
        'attachment; filename="applications.csv"'
    )

    writer = csv.writer(response)
    writer.writerow([
        'Student Name', 'Email', 'Preference 1', 'Preference 2',
        'Category', 'Gender', 'JEE Score', 'CUET Score',
        'Physics', 'Chemistry', 'Math', 'Max Marks',
        'Total Marks', 'Percentage (%)', 'Board', 'School',
        'Applied On'
    ])
    for app in applications:
        writer.writerow([
            app.full_name,
            app.student.email,
            courses_dict.get(app.preference1, app.preference1),
            courses_dict.get(app.preference2, app.preference2),
            app.category,
            app.gender,
            app.jee_score if app.jee_score is not None else 'N/A',
            app.cuet_score if app.cuet_score is not None else 'N/A',
            app.physics_marks,
            app.chemistry_marks,
            app.math_marks,
            app.max_marks,
            app.total_marks,
            app.percentage,
            app.board_name,
            app.school_name,
            app.applied_at.strftime('%d %b %Y'),
        ])
    return response


@staff_member_required(login_url='/login/')
def merit_list(request):
    """Features 5: Course-filtered merit list with top-n."""
    course_filter = request.GET.get('course', 'all')
    top_n = request.GET.get('top_n', '').strip()

    applications = Application.objects.all()
    if course_filter != 'all':
        applications = applications.filter(preference1=course_filter)
    
    # Sort by entrance scores first, then board percentage
    applications = applications.order_by(
        F('jee_score').desc(nulls_last=True),
        F('cuet_score').desc(nulls_last=True),
        F('board_percentage').desc(nulls_last=True),
        '-physics_marks', '-chemistry_marks', '-math_marks'
    )

    if top_n.isdigit() and int(top_n) > 0:
        applications = applications[:int(top_n)]

    courses_dict = _get_courses_dict()
    course_list = list(courses_dict.items())

    return render(request, 'merit_list.html', {
        'applications': applications,
        'course_filter': course_filter,
        'top_n': top_n,
        'courses_dict': courses_dict,
        'course_list': course_list,
    })


@staff_member_required(login_url='/login/')
def download_merit_pdf(request):
    """Feature 6: Download merit list as PDF."""
    course_filter = request.GET.get('course', 'all')
    top_n = request.GET.get('top_n', '').strip()

    applications = Application.objects.all()
    if course_filter != 'all':
        applications = applications.filter(preference1=course_filter)
    
    applications = applications.order_by(
        F('jee_score').desc(nulls_last=True),
        F('cuet_score').desc(nulls_last=True),
        F('board_percentage').desc(nulls_last=True),
        '-physics_marks', '-chemistry_marks', '-math_marks'
    )

    if top_n.isdigit() and int(top_n) > 0:
        applications = applications[:int(top_n)]
        
    approved = list(applications)

    courses_dict = _get_courses_dict()
    course_label = (
        courses_dict.get(course_filter, course_filter)
        if course_filter != 'all'
        else 'All Courses'
    )

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=2 * cm, leftMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'title', fontSize=15, fontName='Helvetica-Bold',
        alignment=1, spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        'subtitle', fontSize=11, fontName='Helvetica',
        alignment=1, spaceAfter=4,
    )
    normal_style = ParagraphStyle(
        'normal', fontSize=9, fontName='Helvetica', spaceAfter=4,
    )
    DARK_BLUE = colors.HexColor('#1a237e')
    LIGHT_BLUE = colors.HexColor('#e8eeff')

    elements = []

    # Header
    elements.append(Paragraph(
        "UNIVERSITY INSTITUTE OF ENGINEERING AND TECHNOLOGY", title_style
    ))
    elements.append(Paragraph(
        "University of Jammu, Janglote, Kathua", subtitle_style
    ))
    elements.append(Paragraph(
        f"B.Tech Merit List — {course_label}", subtitle_style
    ))
    elements.append(HRFlowable(width="100%", thickness=2, color=DARK_BLUE))
    elements.append(Spacer(1, 0.3 * cm))

    # Meta info table
    gen_data = [[
        'Generated On:', date.today().strftime('%d %B %Y'),
        'Course Filter:', course_label,
    ], [
        'Total Candidates:', str(len(approved)),
        'Status:', 'Approved Only',
    ]]
    gen_table = Table(gen_data, colWidths=[4 * cm, 5 * cm, 4 * cm, 5 * cm])
    gen_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BLUE),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(gen_table)
    elements.append(Spacer(1, 0.4 * cm))

    # Merit table
    table_data = [[
        'Rank', 'Student Name', 'Category',
        'Program (Pref. 1)', 'JEE Score', 'Total Marks', '%',
    ]]
    for i, app in enumerate(approved, 1):
        table_data.append([
            str(i),
            app.full_name,
            app.category,
            courses_dict.get(app.preference1, app.preference1),
            str(app.jee_score) if app.jee_score is not None else 'N/A',
            str(app.total_marks),
            f"{app.percentage}%",
        ])

    if len(table_data) == 1:
        elements.append(Paragraph(
            "No approved applications found for the selected filter.",
            normal_style,
        ))
    else:
        merit_table = Table(
            table_data,
            colWidths=[1.2 * cm, 4 * cm, 2.5 * cm, 5 * cm, 2 * cm, 2.5 * cm, 1.8 * cm],
        )
        merit_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), DARK_BLUE),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (4, 0), (-1, -1), 'CENTER'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_BLUE]),
        ]))
        elements.append(merit_table)

    elements.append(Spacer(1, 1 * cm))
    elements.append(Paragraph(
        "This merit list is based on approved applications, sorted by academic performance.",
        normal_style,
    ))

    doc.build(elements)
    buffer.seek(0)

    fname = f'merit_list_{course_filter}.pdf'
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{fname}"'
    return response


# ─── Feature 8: Course Management Views ──────────────────────────────────────

@staff_member_required(login_url='/login/')
def admin_courses(request):
    courses = Course.objects.all()
    add_form = CourseForm()
    edit_course = None
    edit_form = None

    edit_id = request.GET.get('edit')
    if edit_id:
        try:
            edit_course = Course.objects.get(id=edit_id)
            edit_form = CourseForm(initial={
                'name': edit_course.name,
                'code': edit_course.code,
                'total_seats': edit_course.total_seats,
                'available_seats': edit_course.available_seats,
            })
        except Course.DoesNotExist:
            pass

    return render(request, 'admin_courses.html', {
        'courses': courses,
        'add_form': add_form,
        'edit_course': edit_course,
        'edit_form': edit_form,
    })


@staff_member_required(login_url='/login/')
def admin_course_add(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code'].upper().strip()
            if Course.objects.filter(code=code).exists():
                messages.error(
                    request, f'A course with code "{code}" already exists!'
                )
            else:
                Course.objects.create(
                    name=form.cleaned_data['name'],
                    code=code,
                    total_seats=form.cleaned_data['total_seats'],
                    available_seats=form.cleaned_data['available_seats'],
                    is_active=True,
                )
                messages.success(request, f'Course "{code}" added successfully!')
        else:
            messages.error(request, 'Please check all fields and try again.')
    return redirect('admin_courses')


@staff_member_required(login_url='/login/')
def admin_course_edit(request, course_id):
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        messages.error(request, 'Course not found!')
        return redirect('admin_courses')

    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course.name = form.cleaned_data['name']
            course.code = form.cleaned_data['code'].upper().strip()
            course.total_seats = form.cleaned_data['total_seats']
            course.available_seats = form.cleaned_data['available_seats']
            course.save()
            messages.success(
                request, f'Course "{course.code}" updated successfully!'
            )
        else:
            messages.error(request, 'Invalid data. Please try again.')
    return redirect('admin_courses')


@staff_member_required(login_url='/login/')
def admin_course_toggle(request, course_id):
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        messages.error(request, 'Course not found!')
        return redirect('admin_courses')

    course.is_active = not course.is_active
    course.save()
    status_word = 'activated' if course.is_active else 'deactivated'
    messages.success(
        request, f'Course "{course.code}" has been {status_word}.'
    )
    return redirect('admin_courses')


# ─── Existing: Download Individual Application PDF (unchanged logic) ──────────

@login_required(login_url='/login/')
def download_pdf(request, app_id):
    application = Application.objects.get(id=app_id, student=request.user)
    courses_dict = _get_courses_dict()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=2 * cm, leftMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'title', fontSize=16, fontName='Helvetica-Bold', alignment=1, spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        'subtitle', fontSize=12, fontName='Helvetica', alignment=1, spaceAfter=4,
    )
    normal_style = ParagraphStyle(
        'normal', fontSize=10, fontName='Helvetica', spaceAfter=4,
    )

    elements = []

    # Header
    elements.append(Paragraph(
        "UNIVERSITY INSTITUTE OF ENGINEERING AND TECHNOLOGY", title_style
    ))
    elements.append(Paragraph(
        "University of Jammu, Janglote, Kathua", subtitle_style
    ))
    elements.append(Paragraph("B.Tech Admission Application Form", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.darkblue))
    elements.append(Spacer(1, 0.3 * cm))

    # Application Info
    info_data = [[
        'Applied On:', application.applied_at.strftime('%d %B %Y'),
        'Application ID:', str(application.id),
    ]]
    info_table = Table(info_data, colWidths=[4 * cm, 5 * cm, 4 * cm, 5 * cm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightblue),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.3 * cm))

    def section_header(title):
        data = [[title]]
        t = Table(data, colWidths=[17 * cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        return t

    # Program Preferences
    elements.append(section_header('PROGRAM PREFERENCES'))
    elements.append(Spacer(1, 0.2 * cm))
    pref_data = [
        ['Preference 1:', courses_dict.get(application.preference1, application.preference1)],
        ['Preference 2:', courses_dict.get(application.preference2, application.preference2)],
        ['JEE Main Score:', str(application.jee_score) if application.jee_score else 'Not Provided'],
        ['CUET Score:', str(application.cuet_score) if application.cuet_score else 'Not Provided'],
    ]
    pref_table = Table(pref_data, colWidths=[6 * cm, 11 * cm])
    pref_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.lightyellow]),
    ]))
    elements.append(pref_table)
    elements.append(Spacer(1, 0.3 * cm))

    # Personal Details
    elements.append(section_header('PERSONAL DETAILS'))
    elements.append(Spacer(1, 0.2 * cm))
    personal_data = [
        ['Full Name:', application.student.get_full_name(), 'Gender:', application.gender],
        ['Father Name:', application.father_name, 'Mother Name:', application.mother_name],
        ['Date of Birth:', str(application.date_of_birth), 'Category:', application.category],
        ['Phone:', application.phone, 'J&K Resident:', 'Yes' if application.is_jk_resident else 'No'],
    ]
    personal_table = Table(personal_data, colWidths=[4 * cm, 5 * cm, 4 * cm, 4 * cm])
    personal_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.lightyellow]),
    ]))
    elements.append(personal_table)
    elements.append(Spacer(1, 0.2 * cm))

    # Address
    addr_data = [
        ['Correspondence Address:', application.correspondence_address],
        ['Permanent Address:', application.permanent_address],
    ]
    addr_table = Table(addr_data, colWidths=[6 * cm, 11 * cm])
    addr_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.lightyellow]),
    ]))
    elements.append(addr_table)
    elements.append(Spacer(1, 0.3 * cm))

    # Academic Details
    elements.append(section_header('ACADEMIC DETAILS (10+2)'))
    elements.append(Spacer(1, 0.2 * cm))
    academic_data = [
        ['Subject', 'Marks Obtained', 'Maximum Marks', 'Percentage'],
        ['Physics', str(application.physics_marks), str(application.max_marks),
         f"{(application.physics_marks / application.max_marks) * 100:.1f}%"],
        ['Chemistry', str(application.chemistry_marks), str(application.max_marks),
         f"{(application.chemistry_marks / application.max_marks) * 100:.1f}%"],
        ['Mathematics', str(application.math_marks), str(application.max_marks),
         f"{(application.math_marks / application.max_marks) * 100:.1f}%"],
        ['Total', str(application.total_marks), str(application.max_marks * 3),
         f"{application.percentage}%"],
    ]
    academic_table = Table(academic_data, colWidths=[5 * cm, 4 * cm, 4 * cm, 4 * cm])
    academic_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightblue),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.lightyellow]),
    ]))
    elements.append(academic_table)
    elements.append(Spacer(1, 0.2 * cm))

    # School Info
    school_data = [
        ['Board Name:', application.board_name],
        ['School/College:', application.school_name],
    ]
    school_table = Table(school_data, colWidths=[6 * cm, 11 * cm])
    school_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.lightyellow]),
    ]))
    elements.append(school_table)
    elements.append(Spacer(1, 0.3 * cm))

    # Declaration
    elements.append(section_header('DECLARATION'))
    elements.append(Spacer(1, 0.2 * cm))
    elements.append(Paragraph(
        "I hereby declare that all the information furnished above is true and correct to the best "
        "of my knowledge. I understand that any false information may result in cancellation of my "
        "admission.",
        normal_style,
    ))
    elements.append(Spacer(1, 0.5 * cm))

    # Signature — embed the uploaded signature image
    if application.signature:
        try:
            sig_path = application.signature.path
            sig_img = Image(sig_path, width=5 * cm, height=2 * cm)
            sig_data = [['Student Signature:', sig_img, 'Date:', application.applied_at.strftime('%d %B %Y')]]
        except Exception:
            sig_data = [['Student Signature:', '(uploaded)', 'Date:', application.applied_at.strftime('%d %B %Y')]]
    else:
        sig_data = [['Student Signature:', '', 'Date:', application.applied_at.strftime('%d %B %Y')]]
    sig_table = Table(sig_data, colWidths=[4 * cm, 6 * cm, 2 * cm, 5 * cm])
    sig_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(sig_table)

    doc.build(elements)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="Application_{application.student.get_full_name()}_{application.id}.pdf"'
    )
    return response


# ── Payment Views ─────────────────────────────────────────────────────────────

@login_required(login_url='/login/')
def initiate_payment(request):
    """Create a Razorpay order and render the payment page."""
    if request.user.is_staff:
        return redirect('admin_dashboard')
    application = Application.objects.filter(student=request.user).first()
    if not application:
        messages.error(request, 'You need to submit an application before paying.')
        return redirect('apply')

    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )
    order_data = {
        'amount': settings.PAYMENT_AMOUNT,
        'currency': 'INR',
        'receipt': f'app_{application.id}',
        'payment_capture': 1,
    }
    order = client.order.create(data=order_data)

    Payment.objects.update_or_create(
        application=application,
        defaults={
            'razorpay_order_id': order['id'],
            'status': 'pending',
        },
    )

    student = StudentProfile.objects.get(user=request.user)
    return render(request, 'payment.html', {
        'order': order,
        'razorpay_key': settings.RAZORPAY_KEY_ID,
        'amount': settings.PAYMENT_AMOUNT,
        'student': student,
        'application': application,
    })


@csrf_exempt
@login_required(login_url='/login/')
def verify_payment(request):
    """Verify Razorpay HMAC signature and update payment status."""
    if request.method != 'POST':
        return redirect('initiate_payment')

    payment_id = request.POST.get('razorpay_payment_id', '')
    order_id = request.POST.get('razorpay_order_id', '')
    signature = request.POST.get('razorpay_signature', '')

    # HMAC-SHA256 verification
    message = f'{order_id}|{payment_id}'.encode()
    secret = settings.RAZORPAY_KEY_SECRET.encode()
    generated_signature = hmac.new(secret, message, hashlib.sha256).hexdigest()

    application = Application.objects.filter(student=request.user).first()
    payment = Payment.objects.filter(application=application).first()

    if hmac.compare_digest(generated_signature, signature):
        if payment:
            payment.razorpay_payment_id = payment_id
            payment.razorpay_signature = signature
            payment.status = 'paid'
            payment.paid_at = timezone.now()
            payment.save()
        messages.success(request, 'Payment successful! Your fee has been received.')
        return redirect('payment_confirmation')
    else:
        if payment:
            payment.status = 'failed'
            payment.save()
        messages.error(request, 'Payment verification failed. Please try again.')
        return redirect('payment_failed')


@login_required(login_url='/login/')
def payment_confirmation(request):
    """Show payment success page."""
    if request.user.is_staff:
        return redirect('admin_dashboard')
    application = Application.objects.filter(student=request.user).first()
    if not application:
        return redirect('apply')
    try:
        payment = application.payment
    except Payment.DoesNotExist:
        return redirect('initiate_payment')
    if payment.status != 'paid':
        return redirect('initiate_payment')
    return render(request, 'payment_confirmation.html', {'payment': payment})


@login_required(login_url='/login/')
def payment_failed(request):
    """Show payment failure page."""
    return render(request, 'payment_failed.html')


@login_required(login_url='/login/')
def generate_acknowledgment_pdf(request):
    """Generate and download a PDF acknowledgment for a successful payment."""
    if request.user.is_staff:
        return HttpResponseForbidden('Admin cannot download student acknowledgment.')
    application = Application.objects.filter(student=request.user).first()
    if not application:
        return HttpResponseForbidden('No application found.')
    try:
        payment = application.payment
    except Payment.DoesNotExist:
        return HttpResponseForbidden('No payment record found.')
    if payment.status != 'paid':
        return HttpResponseForbidden('Payment not completed.')

    courses_dict = _get_courses_dict()
    buffer = io.BytesIO()
    width, height = A4
    p = canvas.Canvas(buffer, pagesize=A4)

    DARK_BLUE = colors.HexColor('#1a237e')
    ACCENT = colors.HexColor('#1565c0')
    LIGHT_BG = colors.HexColor('#e8eeff')

    # Header band
    p.setFillColor(DARK_BLUE)
    p.rect(0, height - 100, width, 100, fill=1, stroke=0)
    p.setFillColor(colors.white)
    p.setFont('Helvetica-Bold', 16)
    p.drawCentredString(width / 2, height - 45, 'UNIVERSITY INSTITUTE OF ENGINEERING AND TECHNOLOGY')
    p.setFont('Helvetica', 11)
    p.drawCentredString(width / 2, height - 68, 'University of Jammu, Janglote, Kathua')
    p.setFont('Helvetica-Bold', 12)
    p.drawCentredString(width / 2, height - 88, 'Application Acknowledgment')

    # Body
    y = height - 140
    p.setFillColor(ACCENT)
    p.setFont('Helvetica-Bold', 13)
    p.drawString(72, y, 'Payment Receipt & Acknowledgment')
    y -= 8
    p.setStrokeColor(ACCENT)
    p.setLineWidth(1.5)
    p.line(72, y, width - 72, y)
    y -= 30

    def draw_row(label, value, y_pos):
        p.setFillColor(LIGHT_BG)
        p.rect(72, y_pos - 6, width - 144, 24, fill=1, stroke=0)
        p.setFillColor(DARK_BLUE)
        p.setFont('Helvetica-Bold', 10)
        p.drawString(80, y_pos + 4, label)
        p.setFillColor(colors.black)
        p.setFont('Helvetica', 10)
        p.drawString(260, y_pos + 4, str(value))
        return y_pos - 32

    student_name = application.student.get_full_name()
    course = courses_dict.get(application.preference1, application.preference1)
    paid_at_str = payment.paid_at.strftime('%d %B %Y, %I:%M %p') if payment.paid_at else 'N/A'

    y = draw_row('Student Name:', student_name, y)
    y = draw_row('Email:', application.student.email, y)
    y = draw_row('Applied Course (Pref. 1):', course, y)
    y = draw_row('Application ID:', f'APP-{application.id}', y)
    y = draw_row('Razorpay Payment ID:', payment.razorpay_payment_id, y)
    y = draw_row('Amount Paid:', f'\u20b9{payment.amount}', y)
    y = draw_row('Payment Date:', paid_at_str, y)
    y -= 10

    # Status stamp
    p.setFillColor(colors.HexColor('#e8f5e9'))
    p.roundRect(72, y - 30, width - 144, 44, 8, fill=1, stroke=0)
    p.setStrokeColor(colors.HexColor('#2e7d32'))
    p.setLineWidth(1)
    p.roundRect(72, y - 30, width - 144, 44, 8, fill=0, stroke=1)
    p.setFillColor(colors.HexColor('#1b5e20'))
    p.setFont('Helvetica-Bold', 14)
    p.drawCentredString(width / 2, y - 10, 'Status: CONFIRMED ✓')
    y -= 60

    # Footer note
    p.setFillColor(colors.grey)
    p.setFont('Helvetica-Oblique', 9)
    p.drawCentredString(
        width / 2, 60,
        'This is a system-generated acknowledgment. No signature is required.'
    )
    p.setFont('Helvetica', 9)
    p.drawCentredString(width / 2, 45, f'Generated on: {date.today().strftime("%d %B %Y")}')

    p.save()
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="acknowledgment_{application.id}.pdf"'
    )
    return response


# ─── Custom Admin Pages for Admission Round & Merit List PDFs ────────────────

@staff_member_required(login_url='/login/')
def admin_admission_round(request):
    """View to manage the singleton AdmissionRound record."""
    round_record = AdmissionRound.objects.first()
    if not round_record:
        round_record = AdmissionRound.objects.create(current_round='closed')

    if request.method == 'POST':
        form = AdmissionRoundForm(request.POST, instance=round_record)
        if form.is_valid():
            form.save()
            messages.success(request, 'Admission round updated successfully!')
            return redirect('admin_admission_round')
    else:
        form = AdmissionRoundForm(instance=round_record)

    return render(request, 'admin_admission_round.html', {
        'form': form,
        'current_round': round_record.get_current_round_display(),
    })


@staff_member_required(login_url='/login/')
def admin_merit_list_pdfs(request):
    """List all Merit List PDFs and provide form to add new."""
    pdfs = MeritListPDF.objects.all()
    form = MeritListPDFForm()
    return render(request, 'admin_merit_pdfs.html', {
        'pdfs': pdfs,
        'form': form,
    })


@staff_member_required(login_url='/login/')
def admin_merit_list_pdf_add(request):
    """Handle adding a new Merit List PDF."""
    if request.method == 'POST':
        form = MeritListPDFForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Merit list PDF uploaded successfully!')
        else:
            messages.error(request, 'Failed to upload PDF. Please check the file and try again.')
    return redirect('admin_merit_list_pdfs')


@staff_member_required(login_url='/login/')
def admin_merit_list_pdf_toggle(request, pdf_id):
    """Toggle publication status of a Merit List PDF."""
    try:
        pdf = MeritListPDF.objects.get(id=pdf_id)
        pdf.is_published = not pdf.is_published
        pdf.save()
        status = 'published' if pdf.is_published else 'unpublished'
        messages.success(request, f'Merit List "{pdf.title}" has been {status}.')
    except MeritListPDF.DoesNotExist:
        messages.error(request, 'Merit List PDF not found.')
    return redirect('admin_merit_list_pdfs')


@staff_member_required(login_url='/login/')
def admin_merit_list_pdf_delete(request, pdf_id):
    """Delete a Merit List PDF."""
    try:
        pdf = MeritListPDF.objects.get(id=pdf_id)
        title = pdf.title
        pdf.delete()
        messages.success(request, f'Merit List "{title}" has been deleted.')
    except MeritListPDF.DoesNotExist:
        messages.error(request, 'Merit List PDF not found.')
    return redirect('admin_merit_list_pdfs')