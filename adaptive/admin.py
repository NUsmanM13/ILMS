from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline, StackedInline
from .models import Course, Module, Element, Question, Progress

# 1. Element ichida Testni (Question) ko'rsatish
class QuestionInline(StackedInline):
    model = Question
    can_delete = False
    verbose_name = "Bosqich testi"
    verbose_name_plural = "Bosqich testi"
    tab = True # Unfold-da alohida tab bo'lib chiqadi

# 2. Modul ichida Elementlarni ko'rsatish
class ElementInline(TabularInline):
    model = Element
    extra = 1
    show_change_link = True # Element tahrirlash sahifasiga tezkor o'tish
    fields = ["title", "order", "video_url"]

# 3. Kurs (Course) ichida Modullarni ko'rsatish
class ModuleInline(TabularInline):
    model = Module
    extra = 1
    show_change_link = True
    fields = ["title", "order"]

@admin.register(Course)
class CourseAdmin(ModelAdmin):
    list_display = ["title", "created_at", "display_modules_count", "display_total_elements"]
    search_fields = ["title"]
    inlines = [ModuleInline]

    # Kursdagi modullar sonini hisoblash
    def display_modules_count(self, obj):
        return obj.modules.count()
    display_modules_count.short_description = "Modullar"

    # Kursdagi jami elementlar sonini hisoblash
    def display_total_elements(self, obj):
        from .models import Element
        return Element.objects.filter(module__course=obj).count()
    display_total_elements.short_description = "Jami darslar"

@admin.register(Module)
class ModuleAdmin(ModelAdmin):
    list_display = ["title", "course", "order", "display_elements_count"]
    list_filter = ["course"]
    search_fields = ["title"]
    inlines = [ElementInline]

    def display_elements_count(self, obj):
        return obj.elements.count()
    display_elements_count.short_description = "Elementlar"

@admin.register(Element)
class ElementAdmin(ModelAdmin):
    # 'order' birinchi turgani uchun xato bergandi. 
    # 'title'ni birinchi o'ringa qo'yamiz yoki list_display_links ni aniq ko'rsatamiz.
    list_display = ["order", "title", "module", "display_course"]
    list_display_links = ["title"]  # Endi link 'title' ustida bo'ladi
    list_editable = ["order"]       # Tartibni endi bemalol tahrirlasa bo'ladi
    list_filter = ["module__course", "module"]
    search_fields = ["title", "content"]
    inlines = [QuestionInline]
    
    def display_course(self, obj):
        return obj.module.course
    display_course.short_description = "Kurs nomi"

@admin.register(Progress)
class ProgressAdmin(ModelAdmin):
    list_display = ["user", "display_course", "element", "completed"]
    list_filter = ["completed", "element__module__course", "user"]
    search_fields = ["user__username", "element__title"]
    readonly_fields = ["user", "element", "completed"] # Progress o'zgartirilmasligi kerak

    def display_course(self, obj):
        return obj.element.module.course
    display_course.short_description = "Kurs"

# Savollarni alohida tahrirlash uchun
@admin.register(Question)
class QuestionAdmin(ModelAdmin):
    list_display = ["text", "element", "correct_option"]
    list_filter = ["element__module__course"]