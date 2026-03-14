from django.contrib import admin
from unfold.admin import ModelAdmin # Unfold ishlatayotganingiz uchun
from .models import BotKnowledge

@admin.register(BotKnowledge)
class BotKnowledgeAdmin(ModelAdmin):
    list_display = ("keyword", "category", "created_at")
    search_fields = ("keyword", "answer")