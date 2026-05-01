from django.db import models
from django.contrib.auth.models import User


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    date_of_birth = models.DateField()
    address = models.TextField()
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)
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


class Application(models.Model):
    PROGRAM_CHOICES = [
        ('CSE', 'B.Tech Computer Science Engineering'),
        ('CIVIL', 'B.Tech Civil Engineering'),
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
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    # Student
    student = models.ForeignKey(User, on_delete=models.CASCADE)

    # Program Preferences
    preference1 = models.CharField(max_length=10, choices=PROGRAM_CHOICES)
    preference2 = models.CharField(max_length=10, choices=PROGRAM_CHOICES)

    # Exam Scores
    jee_score = models.FloatField(blank=True, null=True)
    cuet_score = models.FloatField(blank=True, null=True)

    # Personal Details
    father_name = models.CharField(max_length=100)
    mother_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
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

    # Documents
    marksheet_10th = models.FileField(upload_to='documents/10th/')
    marksheet_12th = models.FileField(upload_to='documents/12th/')
    category_certificate = models.FileField(upload_to='documents/category/', blank=True, null=True)
    domicile_certificate = models.FileField(upload_to='documents/domicile/', blank=True, null=True)
    signature = models.ImageField(upload_to='signatures/')

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    applied_at = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True)

    @property
    def total_marks(self):
        return self.physics_marks + self.chemistry_marks + self.math_marks

    @property
    def percentage(self):
        if self.max_marks and self.max_marks > 0:
            return round((self.total_marks / (self.max_marks * 3)) * 100, 2)
        return 0.0

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.preference1}"


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
