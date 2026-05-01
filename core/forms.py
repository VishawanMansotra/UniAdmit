from django import forms
from django.contrib.auth.models import User
from .models import StudentProfile


# ─── Existing: Student Registration ───────────────────────────────────────────

class StudentRegistrationForm(forms.Form):
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Enter First Name'
    }))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Enter Last Name'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control', 'placeholder': 'Enter Email'
    }))
    phone = forms.CharField(max_length=15, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Enter Phone Number'
    }))
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={
        'class': 'form-control', 'type': 'date'
    }))
    address = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control', 'placeholder': 'Enter Address', 'rows': 3
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Create Password'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Confirm Password'
    }))
    photo = forms.ImageField(required=False, widget=forms.FileInput(attrs={
        'class': 'form-control'
    }))


# ─── Feature 1: Profile Edit ──────────────────────────────────────────────────

class ProfileEditForm(forms.Form):
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'First Name'
    }))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Last Name'
    }))
    phone = forms.CharField(max_length=15, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Phone Number'
    }))
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={
        'class': 'form-control', 'type': 'date'
    }))
    address = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control', 'rows': 3, 'placeholder': 'Address'
    }))
    photo = forms.ImageField(required=False, widget=forms.FileInput(attrs={
        'class': 'form-control'
    }))


# ─── Feature 8: Course Management Form ───────────────────────────────────────

class CourseForm(forms.Form):
    name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'e.g. B.Tech Computer Science Engineering'
    }))
    code = forms.CharField(max_length=10, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'e.g. CSE (max 10 chars)'
    }))
    total_seats = forms.IntegerField(min_value=1, widget=forms.NumberInput(attrs={
        'class': 'form-control', 'placeholder': 'e.g. 60'
    }))
    available_seats = forms.IntegerField(min_value=0, widget=forms.NumberInput(attrs={
        'class': 'form-control', 'placeholder': 'e.g. 60'
    }))


# ─── Existing (Updated): Application Form with dynamic course choices ─────────

class ApplicationForm(forms.Form):
    DEFAULT_PROGRAM_CHOICES = [
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

    # Preferences — choices set dynamically in __init__
    preference1 = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    preference2 = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    # Exam Scores
    jee_score = forms.FloatField(required=False, widget=forms.NumberInput(attrs={
        'class': 'form-control', 'placeholder': 'Enter JEE Main Score'
    }))
    cuet_score = forms.FloatField(required=False, widget=forms.NumberInput(attrs={
        'class': 'form-control', 'placeholder': 'Enter CUET Score'
    }))

    # Personal
    father_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Enter Father Name'
    }))
    mother_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Enter Mother Name'
    }))
    gender = forms.ChoiceField(choices=GENDER_CHOICES, widget=forms.Select(attrs={
        'class': 'form-select'
    }))
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={
        'class': 'form-control', 'type': 'date'
    }))
    category = forms.ChoiceField(choices=CATEGORY_CHOICES, widget=forms.Select(attrs={
        'class': 'form-select'
    }))

    # Contact
    phone = forms.CharField(max_length=15, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Enter Phone Number'
    }))
    correspondence_address = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control', 'rows': 3,
        'placeholder': 'Enter Correspondence Address'
    }))
    permanent_address = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control', 'rows': 3,
        'placeholder': 'Enter Permanent Address'
    }))
    is_jk_resident = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={
        'class': 'form-check-input'
    }))

    # Academic
    physics_marks = forms.FloatField(widget=forms.NumberInput(attrs={
        'class': 'form-control', 'placeholder': 'Marks obtained'
    }))
    chemistry_marks = forms.FloatField(widget=forms.NumberInput(attrs={
        'class': 'form-control', 'placeholder': 'Marks obtained'
    }))
    math_marks = forms.FloatField(widget=forms.NumberInput(attrs={
        'class': 'form-control', 'placeholder': 'Marks obtained'
    }))
    max_marks = forms.FloatField(widget=forms.NumberInput(attrs={
        'class': 'form-control', 'placeholder': 'Maximum marks per subject'
    }))
    board_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'e.g. JKBOSE, CBSE'
    }))
    school_name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Enter School/College Name'
    }))

    # Documents
    marksheet_10th = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control'}))
    marksheet_12th = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control'}))
    category_certificate = forms.FileField(
        required=False, widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    domicile_certificate = forms.FileField(
        required=False, widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    signature = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Feature 8: Load course choices dynamically from Course model
        try:
            from .models import Course
            courses = Course.objects.filter(is_active=True)
            if courses.exists():
                choices = [(c.code, c.name) for c in courses]
            else:
                choices = self.DEFAULT_PROGRAM_CHOICES
        except Exception:
            choices = self.DEFAULT_PROGRAM_CHOICES
        self.fields['preference1'].choices = choices
        self.fields['preference2'].choices = choices