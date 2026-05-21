from django import forms
from django.contrib.auth.models import User
from django.conf import settings
from .models import StudentProfile


# ─── Existing: Student Registration ───────────────────────────────────────────

class StudentRegistrationForm(forms.Form):
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Enter First Name'
    }))
    middle_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Enter Middle Name'
    }))
    last_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Enter Last Name'
    }))
    gender = forms.ChoiceField(
        choices=[('', 'Select Gender'), ('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control', 'placeholder': 'Enter Email'
    }))
    phone = forms.CharField(max_length=10, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Enter Phone Number'
    }))
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={
        'class': 'form-control', 'type': 'date', 'min': '2000-01-01', 'max': '2025-12-31'
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



    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        allowed_domains = getattr(settings, 'ALLOWED_EMAIL_DOMAINS', [])
        if allowed_domains:
            domain = email.split('@')[-1]
            if domain not in allowed_domains:
                raise forms.ValidationError(
                    f"Email domain '@{domain}' is not allowed. "
                    f"Please use: {', '.join(allowed_domains)}"
                )
        return email

# ─── Feature 1: Profile Edit ──────────────────────────────────────────────────

class ProfileEditForm(forms.Form):
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'First Name'
    }))
    middle_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Middle Name'
    }))
    last_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Last Name'
    }))
    phone = forms.CharField(max_length=10, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Phone Number'
    }))
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={
        'class': 'form-control', 'type': 'date', 'min': '2000-01-01', 'max': '2025-12-31'
    }))
    address = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control', 'rows': 3, 'placeholder': 'Address'
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


# ─── Feature: Admission Round & Merit List Forms ─────────────────────────────

from .models import AdmissionRound, MeritListPDF

class AdmissionRoundForm(forms.ModelForm):
    class Meta:
        model = AdmissionRound
        fields = ['current_round']
        widgets = {
            'current_round': forms.Select(attrs={'class': 'form-select form-select-lg shadow-sm'})
        }

class MeritListPDFForm(forms.ModelForm):
    class Meta:
        model = MeritListPDF
        fields = ['title', 'pdf_file', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Round 1 - CSE Merit List'}),
            'pdf_file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }


# ─── Existing (Updated): Application Form with dynamic course choices ─────────

class ApplicationForm(forms.Form):
    DEFAULT_PROGRAM_CHOICES = [
        ('CSE', 'B.Tech Computer Science Engineering'),
        ('CIVIL', 'B.Tech Civil Engineering'),
        ('ECE', 'B.Tech Electronics and Communication Engineering'),
    ]
    GENDER_CHOICES = [
        ('', 'Select Gender'),
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    CATEGORY_CHOICES = [
        ('', 'Select Category'),
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
    preference3 = forms.ChoiceField(
        choices=[],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    # Exam Scores
    jee_score = forms.DecimalField(max_digits=10, decimal_places=7, max_value=100, min_value=0, required=False, widget=forms.NumberInput(attrs={
        'class': 'form-control', 'placeholder': 'Enter JEE Main Score', 'min': '0', 'max': '100', 'step': '0.0000001'
    }))
    cuet_score = forms.DecimalField(max_digits=10, decimal_places=7, max_value=100, min_value=0, required=False, widget=forms.NumberInput(attrs={
        'class': 'form-control', 'placeholder': 'Enter CUET Score', 'min': '0', 'max': '100', 'step': '0.0000001'
    }))
    board_percentage = forms.DecimalField(
        max_digits=5, decimal_places=2, max_value=100, min_value=0,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 'placeholder': 'Enter Overall 10+2 Percentage (e.g. 85.50)', 'min': '0', 'max': '100', 'step': '0.01'
        })
    )

    # Personal
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Enter First Name'
    }))
    middle_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Enter Middle Name'
    }))
    last_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Enter Last Name'
    }))
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
        'class': 'form-control', 'type': 'date', 'min': '2000-01-01', 'max': '2025-12-31'
    }))
    category = forms.ChoiceField(choices=CATEGORY_CHOICES, widget=forms.Select(attrs={
        'class': 'form-select'
    }))

    # Contact
    phone = forms.CharField(max_length=10, widget=forms.TextInput(attrs={
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
    is_jk_resident = forms.TypedChoiceField(
        choices=[('', 'Select Option'), ('True', 'Yes'), ('False', 'No')],
        coerce=lambda x: x == 'True',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    # Academic
    physics_marks = forms.FloatField(widget=forms.NumberInput(attrs={
        'class': 'form-control', 'placeholder': 'Marks obtained', 'min': '0', 'step': 'any'
    }))
    chemistry_marks = forms.FloatField(widget=forms.NumberInput(attrs={
        'class': 'form-control', 'placeholder': 'Marks obtained', 'min': '0', 'step': 'any'
    }))
    math_marks = forms.FloatField(widget=forms.NumberInput(attrs={
        'class': 'form-control', 'placeholder': 'Marks obtained', 'min': '0', 'step': 'any'
    }))
    max_marks = forms.FloatField(widget=forms.NumberInput(attrs={
        'class': 'form-control', 'placeholder': 'Maximum marks per subject', 'min': '0', 'step': 'any'
    }))
    board_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'e.g. JKBOSE, CBSE'
    }))
    school_name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Enter School/College Name'
    }))

    # Documents — Personal
    passport_photo = forms.ImageField(
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/jpeg,image/jpg'}),
        help_text='Upload a recent passport-size photograph (JPG/JPEG only, 20-50 KB, 200x230 to 400x500 pixels).'
    )
    marksheet_10th = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf'}), help_text='PDF only, 100-500 KB.')
    marksheet_12th = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf'}), help_text='PDF only, 100-500 KB.')
    aadhar_card = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
        help_text='Upload scanned copy of Aadhar Card (PDF only, 100-500 KB).'
    )
    character_certificate = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
        help_text='Character certificate from last attended institution (PDF only, 100-500 KB).'
    )
    category_certificate = forms.FileField(
        required=False, widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
        help_text='PDF only, 100-500 KB.'
    )
    domicile_certificate = forms.FileField(
        required=False, widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
        help_text='PDF only, 100-500 KB.'
    )
    migration_certificate = forms.FileField(
        required=False, widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
        help_text='Required only if passing board is outside J&K (PDF only, 100-500 KB).'
    )
    signature = forms.ImageField(
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/jpeg,image/png,image/jpg'}),
        help_text='Upload clear image of your signature on white paper (JPG/PNG only).'
    )

    # Documents — Score Verification
    entrance_scorecard = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
        help_text='Upload JEE / CUET scorecard (PDF only, 100-500 KB).'
    )

    def _validate_passport_photo(self, file):
        """Validate passport photo for format, size, and dimensions."""
        if file:
            ext = file.name.rsplit('.', 1)[-1].lower()
            if ext not in ['jpg', 'jpeg']:
                raise forms.ValidationError('Passport photograph must be in JPG or JPEG format.')
            
            size_kb = file.size / 1024
            if not (20 <= size_kb <= 50):
                raise forms.ValidationError(f'Passport photograph size must be between 20 KB and 50 KB. Current size is {size_kb:.2f} KB.')
            
            from PIL import Image
            try:
                img = Image.open(file)
                width, height = img.size
                if not (200 <= width <= 400) or not (230 <= height <= 500):
                    raise forms.ValidationError(f'Passport photograph dimensions must be between 200x230 and 400x500 pixels. Current dimensions are {width}x{height} pixels.')
                file.seek(0)
            except forms.ValidationError:
                raise
            except Exception:
                raise forms.ValidationError('Invalid image file.')

    def _validate_document_pdf(self, file, doc_name="Document"):
        """Validate documents/marksheets for PDF format and size."""
        if file:
            ext = file.name.rsplit('.', 1)[-1].lower()
            if ext != 'pdf':
                raise forms.ValidationError(f'{doc_name} must be in PDF format only.')
            
            size_kb = file.size / 1024
            if not (100 <= size_kb <= 500):
                raise forms.ValidationError(f'{doc_name} size must be between 100 KB and 500 KB. Current size is {size_kb:.2f} KB.')

    def _validate_signature(self, file):
        """Validate signature for JPG/PNG format."""
        if file:
            ext = file.name.rsplit('.', 1)[-1].lower()
            if ext not in ['jpg', 'jpeg', 'png']:
                raise forms.ValidationError('Only JPG and PNG image files are allowed for signature.')

    def clean_passport_photo(self):
        f = self.cleaned_data.get('passport_photo')
        self._validate_passport_photo(f)
        return f

    def clean_signature(self):
        f = self.cleaned_data.get('signature')
        self._validate_signature(f)
        return f

    def clean_marksheet_10th(self):
        f = self.cleaned_data.get('marksheet_10th')
        self._validate_document_pdf(f, '10th Marksheet')
        return f

    def clean_marksheet_12th(self):
        f = self.cleaned_data.get('marksheet_12th')
        self._validate_document_pdf(f, '12th Marksheet')
        return f

    def clean_aadhar_card(self):
        f = self.cleaned_data.get('aadhar_card')
        self._validate_document_pdf(f, 'Aadhar Card')
        return f

    def clean_character_certificate(self):
        f = self.cleaned_data.get('character_certificate')
        self._validate_document_pdf(f, 'Character Certificate')
        return f

    def clean_category_certificate(self):
        f = self.cleaned_data.get('category_certificate')
        self._validate_document_pdf(f, 'Category Certificate')
        return f

    def clean_domicile_certificate(self):
        f = self.cleaned_data.get('domicile_certificate')
        self._validate_document_pdf(f, 'Domicile Certificate')
        return f

    def clean_migration_certificate(self):
        f = self.cleaned_data.get('migration_certificate')
        self._validate_document_pdf(f, 'Migration Certificate')
        return f

    def clean_entrance_scorecard(self):
        f = self.cleaned_data.get('entrance_scorecard')
        self._validate_document_pdf(f, 'Entrance Scorecard')
        return f

    def clean(self):
        cleaned_data = super().clean()
        
        max_marks = cleaned_data.get('max_marks')
        
        if max_marks is not None:
            physics_marks = cleaned_data.get('physics_marks')
            chemistry_marks = cleaned_data.get('chemistry_marks')
            math_marks = cleaned_data.get('math_marks')
            
            if physics_marks is not None and physics_marks > max_marks:
                self.add_error('physics_marks', f'Physics marks cannot exceed maximum marks ({max_marks}).')
            if chemistry_marks is not None and chemistry_marks > max_marks:
                self.add_error('chemistry_marks', f'Chemistry marks cannot exceed maximum marks ({max_marks}).')
            if math_marks is not None and math_marks > max_marks:
                self.add_error('math_marks', f'Math marks cannot exceed maximum marks ({max_marks}).')
                
        jee_score = cleaned_data.get('jee_score')
        cuet_score = cleaned_data.get('cuet_score')
        scorecard = cleaned_data.get('entrance_scorecard')
        
        if (jee_score or cuet_score) and not scorecard:
            self.add_error('entrance_scorecard', 'You must upload your Entrance Scorecard if you are providing a JEE or CUET score.')

        return cleaned_data

    def __init__(self, *args, **kwargs):
        current_round = kwargs.pop('current_round', 'round1_jee')
        super().__init__(*args, **kwargs)
        # Load course choices dynamically from Course model
        try:
            from .models import Course
            courses = Course.objects.filter(is_active=True)
            if courses.exists():
                choices = [('', 'Select Preference')] + [(c.code, c.name) for c in courses]
            else:
                choices = [('', 'Select Preference')] + self.DEFAULT_PROGRAM_CHOICES
        except Exception:
            choices = [('', 'Select Preference')] + self.DEFAULT_PROGRAM_CHOICES
        self.fields['preference1'].choices = choices
        self.fields['preference2'].choices = choices
        self.fields['preference3'].choices = choices

        # Dynamically set which score field is required based on the active round
        self.fields['jee_score'].required   = (current_round == 'round1_jee')
        self.fields['cuet_score'].required  = (current_round == 'round2_cuet')
        self.fields['board_percentage'].required = (current_round == 'round3_board')

        # scorecard required for JEE and CUET rounds only
        needs_entrance_docs = current_round in ('round1_jee', 'round2_cuet')
        self.fields['entrance_scorecard'].required = needs_entrance_docs