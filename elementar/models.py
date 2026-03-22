from django.db import models
from django.contrib.auth.models import User

class Lesson(models.Model):
    """Asosiy kurs nomi (masalan: Matematika)"""
    title = models.CharField(max_length=255, verbose_name="Dars nomi")
    description = models.TextField(verbose_name="Tavsif")
    image = models.ImageField(upload_to='lessons/', null=True, blank=True, verbose_name="Rasm")
    created_at = models.DateTimeField(auto_now_add=True)

    def get_progress_percent(self, user):
        """Foydalanuvchining ushbu dars bo'yicha progressini hisoblash"""
        total_elements = Element.objects.filter(module__lesson=self).count()
        if total_elements == 0:
            return 0
        completed_elements = UserProgress.objects.filter(
            user=user, 
            element__module__lesson=self, 
            is_completed=True
        ).count()
        return int((completed_elements / total_elements) * 100)

    def __str__(self):
        return self.title


class Module(models.Model):
    """Dars ichidagi modullar (masalan: 1-bob)"""
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='modules', verbose_name="Dars")
    title = models.CharField(max_length=255, verbose_name="Modul nomi")
    order = models.PositiveIntegerField(default=0, verbose_name="Tartib raqami")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.lesson.title} - {self.title}"


class Element(models.Model):
    """Modul ichidagi konkret mavzu (sahifa)"""
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='elements', verbose_name="Modul")
    title = models.CharField(max_length=255, verbose_name="Mavzu nomi")
    content = models.TextField(help_text="Dars matni (HTML bo'lishi mumkin)", verbose_name="Nazariya")
    video_url = models.URLField(blank=True, null=True, help_text="YouTube video linki", verbose_name="Video URL")
    order = models.PositiveIntegerField(default=0, verbose_name="Tartib raqami")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class Question(models.Model):
    """Darsga tegishli savollar"""
    element = models.ForeignKey(Element, on_delete=models.CASCADE, related_name='questions', verbose_name="Mavzu")
    text = models.TextField(verbose_name="Savol matni")
    option1 = models.CharField(max_length=255, verbose_name="Variant 1")
    option2 = models.CharField(max_length=255, verbose_name="Variant 2")
    option3 = models.CharField(max_length=255, verbose_name="Variant 3")
    option4 = models.CharField(max_length=255, verbose_name="Variant 4")
    correct_option = models.IntegerField(
        choices=[(1, '1-variant'), (2, '2-variant'), (3, '3-variant'), (4, '4-variant')],
        verbose_name="To'g'ri javob"
    )

    def __str__(self):
        return f"{self.element.title} uchun savol: {self.text[:50]}..."


class UserProgress(models.Model):
    """Talabaning har bir mavzuni yopganlik holati va natijasi"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Talaba")
    element = models.ForeignKey(Element, on_delete=models.CASCADE, verbose_name="Mavzu")
    is_completed = models.BooleanField(default=False, verbose_name="Tugatildi")
    score = models.FloatField(default=0, verbose_name="To'plangan ball (%)") # Yangi qo'shilgan maydon
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'element')
        verbose_name = "Foydalanuvchi progressi"
        verbose_name_plural = "Foydalanuvchilar progressi"

    def __str__(self):
        return f"{self.user.username} - {self.element.title} ({self.score}%)"