from django.contrib import admin
from .models import StudentProfile, Application, Course

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'total_seats', 'available_seats', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('code', 'name')

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('student', 'preference1', 'status', 'applied_at')
    list_filter = ('status', 'preference1', 'category')
    search_fields = ('student__first_name', 'student__last_name', 'student__email')

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'date_of_birth')
    search_fields = ('user__first_name', 'user__last_name', 'user__email')
