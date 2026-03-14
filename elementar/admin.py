from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline, StackedInline
from .models import Lesson, Module, Element, Question, UserProgress

# 1. Element ichida Testni (Question) ko'rsatish
class QuestionInline(StackedInline):
    model = Question
    can_delete = False
    verbose_name = "Element testi"
    verbose_name_plural = "Element testi"

# 2. Modul ichida Elementlarni ko'rsatish
class ElementInline(TabularInline):
    model = Element
    extra = 1
    show_change_link = True # Elementning o'ziga o'tish tugmasi
    fields = ["title", "order", "video_url"]

# 3. Dars (Lesson) ichida Modullarni ko'rsatish
class ModuleInline(TabularInline):
    model = Module
    extra = 1
    show_change_link = True
    fields = ["title", "order"]

@admin.register(Lesson)
class LessonAdmin(ModelAdmin):
    list_display = ["title", "created_at", "display_modules_count"]
    search_fields = ["title"]
    inlines = [ModuleInline]

    def display_modules_count(self, obj):
        return obj.modules.count()
    display_modules_count.short_description = "Modullar soni"

@admin.register(Module)
class ModuleAdmin(ModelAdmin):
    list_display = ["title", "lesson", "order", "display_elements_count"]
    list_filter = ["lesson"]
    search_fields = ["title"]
    inlines = [ElementInline]

    def display_elements_count(self, obj):
        return obj.elements.count()
    display_elements_count.short_description = "Elementlar soni"

@admin.register(Element)
class ElementAdmin(ModelAdmin):
    list_display = ["title", "module", "get_lesson", "order"]
    list_filter = ["module__lesson", "module"]
    search_fields = ["title", "content"]
    inlines = [QuestionInline]
    
    # Qaysi darsga tegishli ekanini ko'rsatish
    def get_lesson(self, obj):
        return obj.module.lesson
    get_lesson.short_description = "Dars"

@admin.register(UserProgress)
class UserProgressAdmin(ModelAdmin):
    list_display = ["user", "element", "is_completed", "completed_at"]
    list_filter = ["is_completed", "user", "element__module__lesson"]
    search_fields = ["user__username", "element__title"]
    readonly_fields = ["completed_at"]

# Agar Questionni alohida tahrirlamoqchi bo'lsangiz
@admin.register(Question)
class QuestionAdmin(ModelAdmin):
    list_display = ["text", "element", "correct_option"]
    list_filter = ["element__module__lesson"]