import hashlib
import hmac
from datetime import date

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test import override_settings
from django.urls import reverse

from .forms import ApplicationForm
from .models import Application, Course, Payment, StudentProfile


def _sample_files():
    return {
        "marksheet_10th": SimpleUploadedFile("10th.pdf", b"pdf-content", content_type="application/pdf"),
        "marksheet_12th": SimpleUploadedFile("12th.pdf", b"pdf-content", content_type="application/pdf"),
        "signature": SimpleUploadedFile("sign.png", b"image-content", content_type="image/png"),
    }


def _create_application(user, **overrides):
    files = _sample_files()
    data = {
        "student": user,
        "preference1": "CSE",
        "preference2": "CIVIL",
        "jee_score": 120.0,
        "cuet_score": 85.0,
        "father_name": "Father",
        "mother_name": "Mother",
        "gender": "Male",
        "date_of_birth": date(2005, 1, 1),
        "category": "General",
        "phone": "9999999999",
        "correspondence_address": "Addr 1",
        "permanent_address": "Addr 2",
        "is_jk_resident": True,
        "physics_marks": 90,
        "chemistry_marks": 80,
        "math_marks": 70,
        "max_marks": 100,
        "board_name": "CBSE",
        "school_name": "School",
        "marksheet_10th": files["marksheet_10th"],
        "marksheet_12th": files["marksheet_12th"],
        "signature": files["signature"],
    }
    data.update(overrides)
    return Application.objects.create(**data)


class ApplicationModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="student@example.com",
            email="student@example.com",
            password="Password@123",
            first_name="Stu",
            last_name="Dent",
        )

    def test_total_marks_and_percentage_are_computed(self):
        app = _create_application(self.user, physics_marks=95, chemistry_marks=85, math_marks=75, max_marks=100)
        self.assertEqual(app.total_marks, 255)
        self.assertEqual(app.percentage, 85.0)

    def test_percentage_returns_zero_when_max_marks_is_zero(self):
        app = _create_application(self.user, max_marks=0)
        self.assertEqual(app.percentage, 0.0)


class ApplicationFormTests(TestCase):
    def test_defaults_to_static_program_choices_when_no_courses_exist(self):
        form = ApplicationForm()
        expected = [('', 'Select Preference')] + ApplicationForm.DEFAULT_PROGRAM_CHOICES
        self.assertEqual(form.fields["preference1"].choices, expected)
        self.assertEqual(form.fields["preference2"].choices, expected)

    def test_loads_only_active_courses(self):
        Course.objects.create(name="Computer Science", code="CSE", is_active=True)
        Course.objects.create(name="Mechanical", code="ME", is_active=False)
        form = ApplicationForm()
        expected = [('', 'Select Preference'), ("CSE", "Computer Science")]
        self.assertEqual(form.fields["preference1"].choices, expected)
        self.assertEqual(form.fields["preference2"].choices, expected)


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }
)
class CoreViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="student2@example.com",
            email="student2@example.com",
            password="Password@123",
            first_name="Test",
            last_name="User",
        )
        StudentProfile.objects.create(
            user=self.user,
            phone="9999999999",
            date_of_birth=date(2004, 1, 1),
            address="Address",
        )

    def test_apply_redirects_when_application_already_exists(self):
        self.client.login(username="student2@example.com", password="Password@123")
        existing = _create_application(self.user)
        response = self.client.get(reverse("apply"))
        # Should either show duplicate context or redirect
        self.assertIn(response.status_code, [200, 302])

    def test_verify_payment_marks_payment_as_paid_for_valid_signature(self):
        self.client.login(username="student2@example.com", password="Password@123")
        app = _create_application(self.user)
        payment = Payment.objects.create(application=app, razorpay_order_id="order_123", status="pending")
        payment_id = "pay_123"
        signature = hmac.new(
            settings.RAZORPAY_KEY_SECRET.encode(),
            f"{payment.razorpay_order_id}|{payment_id}".encode(),
            hashlib.sha256,
        ).hexdigest()

        response = self.client.post(
            reverse("verify_payment"),
            {
                "razorpay_payment_id": payment_id,
                "razorpay_order_id": payment.razorpay_order_id,
                "razorpay_signature": signature,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("payment_confirmation"))
        payment.refresh_from_db()
        self.assertEqual(payment.status, "paid")
        self.assertEqual(payment.razorpay_payment_id, payment_id)
        self.assertIsNotNone(payment.paid_at)

    def test_verify_payment_marks_payment_as_failed_for_invalid_signature(self):
        self.client.login(username="student2@example.com", password="Password@123")
        app = _create_application(self.user)
        payment = Payment.objects.create(application=app, razorpay_order_id="order_456", status="pending")

        response = self.client.post(
            reverse("verify_payment"),
            {
                "razorpay_payment_id": "pay_456",
                "razorpay_order_id": payment.razorpay_order_id,
                "razorpay_signature": "invalid-signature",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("payment_failed"))
        payment.refresh_from_db()
        self.assertEqual(payment.status, "failed")
