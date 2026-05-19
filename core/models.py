from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

def validate_dob_year(value):
    if value.year < 2000:
        raise ValidationError("Date of birth must be from year 2000 onwards.")



class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=15)
    gender = models.CharField(max_length=10, blank=True, null=True)
    date_of_birth = models.DateField(validators=[validate_dob_year])
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.get_full_name()


class Course(models.Model):
    """Feature 8: Dynamic course management"""
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=10, unique=True)
    total_seats = models.IntegerField(default=60)
    available_seats = models.IntegerField(default=60)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return f"{self.code} — {self.name}"


class AdmissionRound(models.Model):
    """
    Singleton model — admin creates ONE record and updates it to control
    which admission round is currently active.
    """
    ROUND_CHOICES = [
        ('closed',       'Closed — No Applications Accepted'),
        ('round1_jee',   'Round 1 — JEE Mains 2026'),
        ('round2_cuet',  'Round 2 — CUET UG'),
        ('round3_board', 'Round 3 — 10+2 Board Percentage'),
    ]
    current_round = models.CharField(
        max_length=20,
        choices=ROUND_CHOICES,
        default='closed',
        help_text='Select the active admission round. Only one record should exist.'
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Admission Round Control'
        verbose_name_plural = 'Admission Round Control'

    def __str__(self):
        return f"Active Round: {self.get_current_round_display()}"

    @classmethod
    def get_active(cls):
        """Returns the current round string, defaults to 'closed' if no record exists."""
        obj = cls.objects.first()
        return obj.current_round if obj else 'closed'


class Application(models.Model):
    PROGRAM_CHOICES = [
        ('CSE', 'B.Tech Computer Science Engineering'),
        ('CIVIL', 'B.Tech Civil Engineering'),
        ('ECE', 'B.Tech Electronics and Communication Engineering'),
    ]
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    CATEGORY_CHOICES = [
        ('General', 'General'),
        ('OBC', 'OBC'),
        ('SC', 'SC'),
        ('ST', 'ST'),
        ('EWS', 'EWS'),
        ('PWD', 'PWD'),
    ]
    # Student
    student = models.ForeignKey(User, on_delete=models.CASCADE)

    # Program Preferences
    preference1 = models.CharField(max_length=10, choices=PROGRAM_CHOICES)
    preference2 = models.CharField(max_length=10, choices=PROGRAM_CHOICES)
    preference3 = models.CharField(max_length=10, choices=PROGRAM_CHOICES, blank=True, null=True)

    # Admission Round tracking
    applied_round = models.CharField(
        max_length=20,
        default='round1_jee',
        help_text='Which round this application was submitted under.'
    )

    # Exam Scores
    jee_score = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    cuet_score = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    board_percentage = models.DecimalField(
        max_digits=5, decimal_places=2,
        blank=True, null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Overall 10+2 board percentage (for Round 3 only).'
    )

    # Personal Details
    first_name = models.CharField(max_length=100, blank=True, null=True)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    father_name = models.CharField(max_length=100)
    mother_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(validators=[validate_dob_year])
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

    # Contact
    phone = models.CharField(max_length=15)
    correspondence_address = models.TextField()
    permanent_address = models.TextField()
    is_jk_resident = models.BooleanField(default=False)

    # Academic Details
    physics_marks = models.FloatField()
    chemistry_marks = models.FloatField()
    math_marks = models.FloatField()
    max_marks = models.FloatField()
    board_name = models.CharField(max_length=100)
    school_name = models.CharField(max_length=200)

    # Documents — Personal
    passport_photo = models.ImageField(upload_to='documents/photos/', blank=True, null=True)
    marksheet_10th = models.FileField(upload_to='documents/10th/')
    marksheet_12th = models.FileField(upload_to='documents/12th/')
    aadhar_card = models.FileField(upload_to='documents/aadhar/', blank=True, null=True)
    character_certificate = models.FileField(upload_to='documents/character/', blank=True, null=True)
    category_certificate = models.FileField(upload_to='documents/category/', blank=True, null=True)
    domicile_certificate = models.FileField(upload_to='documents/domicile/', blank=True, null=True)
    migration_certificate = models.FileField(upload_to='documents/migration/', blank=True, null=True)
    signature = models.ImageField(upload_to='signatures/')

    # Documents — Score Verification
    entrance_scorecard = models.FileField(upload_to='documents/scorecard/', blank=True, null=True,
        help_text='Upload JEE / CUET scorecard PDF or image.')

    applied_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_marks(self):
        return self.physics_marks + self.chemistry_marks + self.math_marks

    @property
    def percentage(self):
        if self.max_marks and self.max_marks > 0:
            return round((self.total_marks / (self.max_marks * 3)) * 100, 2)
        return 0.0

    @property
    def full_name(self):
        parts = [
            self.first_name or self.student.first_name,
            self.middle_name,
            self.last_name or self.student.last_name
        ]
        return " ".join([p for p in parts if p]).strip()

    def __str__(self):
        return f"{self.full_name} - {self.preference1}"


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]
    application = models.OneToOneField(
        Application, on_delete=models.CASCADE, related_name='payment'
    )
    razorpay_order_id = models.CharField(max_length=100, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True)
    razorpay_signature = models.CharField(max_length=255, blank=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2, default=500.00)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment({self.application.student.get_full_name()} - {self.status})"


class MeritListPDF(models.Model):
    title = models.CharField(max_length=200, help_text="e.g., Round 1 - CSE Merit List")
    pdf_file = models.FileField(upload_to='merit_lists/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True, help_text="Show on homepage?")

    class Meta:
        verbose_name = "Merit List PDF"
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title
