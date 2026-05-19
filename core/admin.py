from django.contrib import admin
from django.utils.html import format_html
from .models import StudentProfile, Application, Course, AdmissionRound, MeritListPDF

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'total_seats', 'available_seats', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('code', 'name')

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('student', 'preference1', 'applied_at')
    list_filter = ('preference1', 'category')
    search_fields = ('student__first_name', 'student__last_name', 'student__email')

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'date_of_birth')
    search_fields = ('user__first_name', 'user__last_name', 'user__email')


@admin.register(AdmissionRound)
class AdmissionRoundAdmin(admin.ModelAdmin):
    list_display = ('current_round_display', 'updated_at')
    readonly_fields = ('updated_at',)

    def current_round_display(self, obj):
        colors = {
            'closed':       '#dc3545',
            'round1_jee':   '#0d6efd',
            'round2_cuet':  '#198754',
            'round3_board': '#fd7e14',
        }
        color = colors.get(obj.current_round, '#6c757d')
        return format_html(
            '<span style="color:white;background:{};padding:4px 10px;border-radius:4px;font-weight:bold;">{}</span>',
            color,
            obj.get_current_round_display()
        )
    current_round_display.short_description = 'Active Round'

    def has_add_permission(self, request):
        # Only allow one record
        return not AdmissionRound.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(MeritListPDF)
class MeritListPDFAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_at', 'is_published')
    list_filter = ('is_published',)
    search_fields = ('title',)
