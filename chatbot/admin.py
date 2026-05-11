from django.contrib import admin
from django.utils.html import format_html
from .models import CollegeKnowledge, ChatSession, ChatMessage, ChatFeedback, UnansweredQuery


# ─────────────────────────────────────────────
#  College Knowledge Base Admin
#  (This is where you TRAIN the chatbot)
# ─────────────────────────────────────────────
@admin.register(CollegeKnowledge)
class CollegeKnowledgeAdmin(admin.ModelAdmin):
    list_display = ['topic', 'category', 'is_active', 'updated_at', 'preview']
    list_filter = ['category', 'is_active']
    search_fields = ['topic', 'information']
    list_editable = ['is_active']
    ordering = ['category', 'topic']

    fieldsets = (
        ('Topic Information', {
            'fields': ('category', 'topic'),
            'description': 'Choose a category and give a clear topic title.'
        }),
        ('Knowledge Content', {
            'fields': ('information',),
            'description': 'Enter detailed information about this topic. '
                           'The chatbot will use this to answer student queries.'
        }),
        ('Status', {
            'fields': ('is_active',),
        }),
    )

    def preview(self, obj):
        return obj.information[:80] + '...' if len(obj.information) > 80 else obj.information
    preview.short_description = 'Preview'

    # Admin action: Bulk activate/deactivate
    actions = ['activate_entries', 'deactivate_entries']

    def activate_entries(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} entries activated.")
    activate_entries.short_description = "✅ Activate selected entries"

    def deactivate_entries(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} entries deactivated.")
    deactivate_entries.short_description = "❌ Deactivate selected entries"


# ─────────────────────────────────────────────
#  Unanswered Queries Admin
#  (Review these to improve chatbot)
# ─────────────────────────────────────────────
@admin.register(UnansweredQuery)
class UnansweredQueryAdmin(admin.ModelAdmin):
    list_display = ['query_preview', 'frequency', 'is_resolved', 'created_at', 'action_needed']
    list_filter = ['is_resolved', 'created_at']
    search_fields = ['query']
    list_editable = ['is_resolved']
    ordering = ['-frequency', '-created_at']

    fieldsets = (
        ('Query Details', {
            'fields': ('query', 'frequency', 'session'),
        }),
        ('Resolution', {
            'fields': ('is_resolved', 'resolution_note'),
            'description': 'Mark as resolved after adding the answer to College Knowledge Base.'
        }),
    )

    def query_preview(self, obj):
        return obj.query[:80] + '...' if len(obj.query) > 80 else obj.query
    query_preview.short_description = 'Student Query'

    def action_needed(self, obj):
        if not obj.is_resolved:
            return format_html('<span style="color:red; font-weight:bold;">⚠️ Add to Knowledge Base</span>')
        return format_html('<span style="color:green;">✅ Resolved</span>')
    action_needed.short_description = 'Action'

    actions = ['mark_resolved']

    def mark_resolved(self, request, queryset):
        queryset.update(is_resolved=True)
        self.message_user(request, f"{queryset.count()} queries marked as resolved.")
    mark_resolved.short_description = "✅ Mark selected as resolved"


# ─────────────────────────────────────────────
#  Chat Message Inline
# ─────────────────────────────────────────────
class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    fields = ['sender', 'message', 'timestamp']
    readonly_fields = ['sender', 'message', 'timestamp']
    extra = 0
    can_delete = False
    max_num = 20

    def has_add_permission(self, request, obj=None):
        return False


# ─────────────────────────────────────────────
#  Chat Session Admin
# ─────────────────────────────────────────────
@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id_short', 'started_at', 'last_active', 'message_count']
    readonly_fields = ['session_id', 'started_at', 'last_active']
    inlines = [ChatMessageInline]

    def session_id_short(self, obj):
        return obj.session_id[:12] + '...'
    session_id_short.short_description = 'Session ID'

    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Messages'

    def has_add_permission(self, request):
        return False


# ─────────────────────────────────────────────
#  Feedback Admin
# ─────────────────────────────────────────────
@admin.register(ChatFeedback)
class ChatFeedbackAdmin(admin.ModelAdmin):
    list_display = ['message_preview', 'rating_display', 'comment', 'created_at']
    list_filter = ['rating', 'created_at']
    readonly_fields = ['message', 'created_at']

    def message_preview(self, obj):
        return obj.message.message[:60]
    message_preview.short_description = 'Bot Response'

    def rating_display(self, obj):
        stars = {1: '👎 Not Helpful', 2: '😐 Somewhat Helpful', 3: '👍 Very Helpful'}
        return stars.get(obj.rating, obj.rating)
    rating_display.short_description = 'Rating'

    def has_add_permission(self, request):
        return False
