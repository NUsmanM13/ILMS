from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline, StackedInline
from unfold.decorators import display
from .models import Course, Module, Topic, Element, Question, UserProgress

# ----------------------------------------------------------------
# INLINES (Ichma-ich ko'rinishlar)
# ----------------------------------------------------------------

class QuestionInline(StackedInline):
    """Element (Daraja) ichida savollarni ko'rsatish"""
    model = Question
    extra = 1
    tab = True # Unfold-da alohida tabga ajratadi
    verbose_name = "Test savoli"
    verbose_name_plural = "Test savollari"

class ElementInline(TabularInline):
    """Mavzu (Topic) ichida uning 3 ta darajasini ko'rsatish"""
    model = Element
    extra = 0 # Avtomatik 3 ta daraja bo'lishi shart emas, lekin qo'shsa bo'ladi
    show_change_link = True
    fields = ["difficulty", "video_url"]
    tab = True

class TopicInline(TabularInline):
    """Modul ichida mavzularni ko'rsatish"""
    model = Topic
    extra = 1
    show_change_link = True
    fields = ["title", "order"]

class ModuleInline(TabularInline):
    """Kurs ichida modullarni ko'rsatish"""
    model = Module
    extra = 1
    show_change_link = True
    fields = ["title", "order"]

# ----------------------------------------------------------------
# MODEL ADMINS
# ----------------------------------------------------------------

@admin.register(Course)
class CourseAdmin(ModelAdmin):
    list_display = ["title", "created_at", "display_modules_count", "display_total_topics"]
    search_fields = ["title"]
    inlines = [ModuleInline]

    @display(description="Modullar soni", label=True)
    def display_modules_count(self, obj):
        return obj.modules.count()

    @display(description="Jami Mavzular", label=True)
    def display_total_topics(self, obj):
        return Topic.objects.filter(module__course=obj).count()


@admin.register(Module)
class ModuleAdmin(ModelAdmin):
    list_display = ["title", "course", "order", "display_topics_count"]
    list_filter = ["course"]
    search_fields = ["title"]
    inlines = [TopicInline]

    @display(description="Mavzular soni", label=True)
    def display_topics_count(self, obj):
        return obj.topics.count()


@admin.register(Topic)
class TopicAdmin(ModelAdmin):
    list_display = ["title", "module", "order", "display_elements_count"]
    list_filter = ["module__course", "module"]
    search_fields = ["title"]
    inlines = [ElementInline]

    @display(description="Darajalar soni", label=True)
    def display_elements_count(self, obj):
        return obj.elements.count()


@admin.register(Element)
class ElementAdmin(ModelAdmin):
    list_display = ["topic", "difficulty", "display_module", "display_course", "display_questions_count"]
    list_display_links = ["topic"]
    list_filter = ["difficulty", "topic__module__course", "topic__module"]
    search_fields = ["topic__title", "content"]
    inlines = [QuestionInline]
    
    @display(description="Modul")
    def display_module(self, obj):
        return obj.topic.module.title

    @display(description="Kurs")
    def display_course(self, obj):
        return obj.topic.module.course.title

    @display(description="Savollar", label=True)
    def display_questions_count(self, obj):
        return obj.questions.count()


@admin.register(UserProgress)
class UserProgressAdmin(ModelAdmin):
    # Modelda highest_level ga o'zgartirganimiz uchun bu yerda ham yangiladik
    list_display = ["user", "topic", "highest_level", "score", "is_passed", "updated_at"]
    list_filter = ["is_passed", "highest_level", "topic__module__course"]
    search_fields = ["user__username", "topic__title"]
    
    # Progress avtomatik hisoblangani uchun uni admin panelda o'zgartirib bo'lmaydi (faqat ko'rish mumkin)
    readonly_fields = ["user", "topic", "element", "score", "is_passed", "highest_level", "updated_at"]

    def has_add_permission(self, request):
        return False # Admin progress qo'sha olmaydi


@admin.register(Question)
class QuestionAdmin(ModelAdmin):
    list_display = ["text", "display_element", "correct_option"]
    list_filter = ["element__difficulty", "element__topic__module__course"]
    search_fields = ["text"]

    @display(description="Mavzu va Daraja")
    def display_element(self, obj):
        return f"{obj.element.topic.title} ({obj.element.difficulty}-daraja)"