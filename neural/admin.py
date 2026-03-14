from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline, StackedInline
from .models import AIPath, Module, Element, Quiz, NeuralProgress

# 1. Modullarni AIPath ichida ko'rsatish uchun Inline
class ModuleInline(TabularInline):
    model = Module
    extra = 1
    show_change_link = True
    fields = ["title", "order"]

# 2. Elementlarni Modul ichida ko'rsatish uchun Inline
class ElementInline(TabularInline):
    model = Element
    extra = 1
    show_change_link = True
    fields = ["title", "is_essential", "order"]

# 3. Testni Element ichida ko'rsatish uchun Inline
class QuizInline(StackedInline):
    model = Quiz
    can_delete = False
    tab = True

@admin.register(AIPath)
class AIPathAdmin(ModelAdmin):
    list_display = ["title", "created_at", "display_essential_count"]
    # BU YERDA XATO EDI: Endi aniq klass (ModuleInline) berildi
    inlines = [ModuleInline]
    
    def display_essential_count(self, obj):
        # Muhim elementlarni hisoblash
        return Element.objects.filter(module__path=obj, is_essential=True).count()
    display_essential_count.short_description = "Muhim elementlar"

@admin.register(Module)
class ModuleAdmin(ModelAdmin):
    list_display = ["title", "path", "order"]
    list_filter = ["path"]
    inlines = [ElementInline]

@admin.register(Element)
class ElementAdmin(ModelAdmin):
    list_display = ["title", "module", "is_essential", "order"]
    list_display_links = ["title"] # Linkni title ga qo'yamiz
    list_filter = ["is_essential", "module__path"]
    list_editable = ["order", "is_essential"] # Tartib va muhimlikni ro'yxatda tahrirlash
    inlines = [QuizInline]

@admin.register(NeuralProgress)
class NeuralProgressAdmin(ModelAdmin):
    list_display = ["user", "element", "completed"]


@admin.register(Quiz)
class QuizAdmin(ModelAdmin):
    list_display = ["question", "element", "correct"]
    list_filter = ["element__module__path"]
    search_fields = ["question"]