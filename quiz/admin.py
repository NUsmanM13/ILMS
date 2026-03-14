from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Subject, Question, ExamSession

@admin.register(Subject)
class SubjectAdmin(ModelAdmin):
    list_display = ["name"]

@admin.register(Question)
class QuestionAdmin(ModelAdmin):
    list_display = ["text", "subject", "level", "coefficient"]
    list_filter = ["subject", "level"]
    search_fields = ["text"]

@admin.register(ExamSession)
class ExamSessionAdmin(ModelAdmin):
    list_display = ["user", "subject", "exam_type", "score", "final_grade", "is_finished"]
    list_filter = ["exam_type", "is_finished"]