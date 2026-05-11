from django.db import models

# Link this to your existing Student model from core app
# from core.models import Student  # uncomment this line in your project


class CollegeKnowledge(models.Model):
    """
    This is the TRAINING DATA for your chatbot.
    Add info about college here → chatbot learns from it automatically.
    """
    CATEGORY_CHOICES = [
        ('admissions', 'Admissions'),
        ('courses', 'Courses & Programs'),
        ('facilities', 'Campus Facilities'),
        ('fees', 'Fee Structure'),
        ('eligibility', 'Eligibility Criteria'),
        ('placement', 'Placement & Career'),
        ('hostel', 'Hostel & Accommodation'),
        ('contact', 'Contact & Location'),
        ('exam', 'Exams & Results'),
        ('general', 'General Information'),
    ]

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    topic = models.CharField(max_length=200, help_text="Short topic title e.g. 'CSE Fees 2025'")
    information = models.TextField(help_text="Detailed information about this topic")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'topic']
        verbose_name = 'College Knowledge'
        verbose_name_plural = 'College Knowledge Base'

    def __str__(self):
        return f"[{self.get_category_display()}] {self.topic}"


class ChatSession(models.Model):
    """Stores each chat conversation"""
    # student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(max_length=100, unique=True)
    started_at = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Session {self.session_id[:8]}... ({self.started_at.strftime('%d-%m-%Y %H:%M')})"


class ChatMessage(models.Model):
    """Stores individual messages in a session"""
    SENDER_CHOICES = [
        ('user', 'User'),
        ('bot', 'Bot'),
    ]

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender}: {self.message[:50]}"


class ChatFeedback(models.Model):
    """
    Students can rate chatbot responses.
    This helps you identify which answers need improvement.
    """
    RATING_CHOICES = [
        (1, '👎 Not Helpful'),
        (2, '😐 Somewhat Helpful'),
        (3, '👍 Very Helpful'),
    ]

    message = models.OneToOneField(ChatMessage, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback: {self.rating}/3 for message {self.message.id}"


class UnansweredQuery(models.Model):
    """
    Tracks questions the bot couldn't answer well.
    Use this to improve your knowledge base.
    """
    query = models.TextField()
    session = models.ForeignKey(ChatSession, on_delete=models.SET_NULL, null=True)
    frequency = models.IntegerField(default=1, help_text="How many times asked")
    is_resolved = models.BooleanField(default=False)
    resolution_note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-frequency']
        verbose_name = 'Unanswered Query'
        verbose_name_plural = 'Unanswered Queries'

    def __str__(self):
        return f"Query: {self.query[:60]} (asked {self.frequency}x)"
