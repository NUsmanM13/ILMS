from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Folder, Material, Submission

# 1. Folder ichida Materiallarni ko'rsatish uchun Inline
class MaterialInline(TabularInline):
    model = Material
    extra = 1
    tab = True  # Unfold'da ma'lumotlarni tab ko'rinishida ajratish uchun
    fields = ["title", "file", "is_assignment"]

# 2. Folder ichida Talabalar javoblarini ko'rish uchun Inline
class SubmissionInline(TabularInline):
    model = Submission
    extra = 0
    readonly_fields = ["user", "file", "uploaded_at", "comment"]
    can_delete = False # Admin bu yerdan o'chirib yubormasligi uchun

@admin.register(Folder)
class FolderAdmin(ModelAdmin):
    list_display = ["name", "created_at", "display_materials_count", "display_submissions_count"]
    search_fields = ["name"]
    list_filter = ["created_at"]
    inlines = [MaterialInline, SubmissionInline]

    # Unfold uchun maxsus: qatorlar sonini hisoblash metodlari
    def display_materials_count(self, obj):
        return obj.materials.count()
    display_materials_count.short_description = "Materiallar soni"

    def display_submissions_count(self, obj):
        return obj.submissions.count()
    display_submissions_count.short_description = "Javoblar soni"


@admin.register(Material)
class MaterialAdmin(ModelAdmin):
    list_display = ["title", "folder", "is_assignment", "uploaded_at"]
    list_filter = ["folder", "is_assignment", "uploaded_at"]
    search_fields = ["title", "folder__name"]
    list_editable = ["is_assignment"] # Ro'yxatning o'zidayoq o'zgartirish imkoniyati


@admin.register(Submission)
class SubmissionAdmin(ModelAdmin):
    list_display = ["user", "folder", "uploaded_at"]
    list_filter = ["folder", "user", "uploaded_at"]
    search_fields = ["user__username", "folder__name", "comment"]
    readonly_fields = ["user", "folder", "file", "comment", "uploaded_at"] # Javoblar o'zgartirilmasligi kerak

    # Unfold'da filtrlarni chiroyli chiqarish
    list_filter_submit = True