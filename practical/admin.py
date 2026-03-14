from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Assignment, Submission
from django.utils import timezone

class SubmissionInline(TabularInline):
    model = Submission
    extra = 0
    readonly_fields = ['user', 'file', 'submitted_at']
    fields = ['user', 'file', 'grade', 'teacher_comment', 'is_graded']

@admin.register(Assignment)
class AssignmentAdmin(ModelAdmin):
    list_display = ['title', 'task_type', 'deadline', 'display_submissions']
    list_filter = ['task_type']
    inlines = [SubmissionInline]

    def display_submissions(self, obj):
        return obj.submissions.count()
    display_submissions.short_description = "Javoblar soni"

@admin.register(Submission)
class SubmissionAdmin(ModelAdmin):
    list_display = ['user', 'assignment', 'grade', 'is_graded', 'submitted_at']
    list_filter = ['is_graded', 'assignment__task_type']
    search_fields = ['user__username', 'assignment__title']
    list_editable = ['grade', 'is_graded'] # To'g'ridan-to'g'ri ro'yxatda baholash

    def save_model(self, request, obj, form, change):
        if obj.grade is not None and not obj.graded_at:
            obj.graded_at = timezone.now()
            obj.is_graded = True
        super().save_model(request, obj, form, change)