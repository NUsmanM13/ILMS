from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Course(models.Model):
    """O'quv kursi: Umumiy konteyner"""
    title = models.CharField(max_length=255, verbose_name="Kurs nomi")
    description = models.TextField(verbose_name="Kurs haqida")
    image = models.ImageField(upload_to='adaptive/courses/', null=True, blank=True, verbose_name="Kurs rasmi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")

    class Meta:
        verbose_name = "Kurs"
        verbose_name_plural = "Kurslar"

    def __str__(self):
        return self.title


class Module(models.Model):
    """Kurs ichidagi modullar (masalan: 1-bob, 2-bob)"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules', verbose_name="Kurs")
    title = models.CharField(max_length=255, verbose_name="Modul nomi")
    order = models.PositiveIntegerField(default=0, verbose_name="Tartib raqami")

    class Meta:
        ordering = ['order']
        verbose_name = "Modul"
        verbose_name_plural = "Modullar"

    def __str__(self):
        return f"{self.course.title} | {self.title}"


class Topic(models.Model):
    """Mavzu: Bir mavzu ostida bir nechta qiyinlikdagi darslar (Element) bo'ladi"""
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='topics', verbose_name="Modul")
    title = models.CharField(max_length=255, verbose_name="Mavzu nomi")
    order = models.PositiveIntegerField(default=0, verbose_name="Tartib raqami")

    class Meta:
        ordering = ['order']
        verbose_name = "Mavzu"
        verbose_name_plural = "Mavzular"

    def __str__(self):
        return self.title


class Element(models.Model):
    """
    Dars (Element): Bir mavzuning 3 xil qiyinlik darajasi.
    Adaptivlik aynan shu darajalar orqali boshqariladi.
    """
    LEVEL_CHOICES = [
        (3, 'Oddiy (3-baholik)'),
        (4, 'Oʻrta (4-baholik)'),
        (5, 'Murakkab (5-baholik)'),
    ]
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='elements', verbose_name="Mavzu")
    difficulty = models.IntegerField(choices=LEVEL_CHOICES, default=3, verbose_name="Qiyinlik darajasi")
    content = models.TextField(verbose_name="Dars matni (Nazariya)")
    video_url = models.URLField(blank=True, null=True, verbose_name="Video darslik URL")

    class Meta:
        verbose_name = "Dars elementi"
        verbose_name_plural = "Dars elementlari"
        unique_together = ('topic', 'difficulty') # Bitta mavzuda bitta darajadan faqat bitta dars bo'lishi shart

    def __str__(self):
        return f"{self.topic.title} - {self.get_difficulty_display()}"


class Question(models.Model):
    """Har bir Element (dars darajasi) uchun maxsus testlar"""
    element = models.ForeignKey(Element, on_delete=models.CASCADE, related_name='questions', verbose_name="Dars darajasi")
    text = models.TextField(verbose_name="Savol matni")
    option1 = models.CharField(max_length=255, verbose_name="Variant 1")
    option2 = models.CharField(max_length=255, verbose_name="Variant 2")
    option3 = models.CharField(max_length=255, verbose_name="Variant 3")
    option4 = models.CharField(max_length=255, verbose_name="Variant 4")
    correct_option = models.IntegerField(
        choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4')],
        verbose_name="To'g'ri javob raqami"
    )

    class Meta:
        verbose_name = "Savol"
        verbose_name_plural = "Savollar"


class UserProgress(models.Model):
    """
    Foydalanuvchi progressi:
    Bu model talabaning har bir mavzu bo'yicha eng oxirgi ko'rsatkichi va 
    erishgan eng yuqori darajasini saqlaydi.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='adaptive_progress', verbose_name="Talaba")
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, verbose_name="Mavzu")
    
    # Oxirgi muvaffaqiyatli topshirgan dars darajasi (elementi)
    element = models.ForeignKey(Element, on_delete=models.CASCADE, verbose_name="Oxirgi yopilgan dars")
    
    score = models.FloatField(default=0, verbose_name="To'plangan ball (%)")
    is_passed = models.BooleanField(default=False, verbose_name="Mavzu yopildimi?")
    
    # Talabaning ushbu mavzu bo'yicha erishgan eng yuqori darajasi (3, 4 yoki 5)
    # Bu maydon talaba 3-darajani yopgandan keyin 5-darajaga o'ta olganini bilish uchun kerak
    highest_level = models.IntegerField(default=3, verbose_name="Erishilgan eng yuqori daraja")
    
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Oxirgi yangilanish")

    class Meta:
        unique_together = ('user', 'topic') # Har bir talaba uchun har bir mavzuda bitta progress bo'ladi
        verbose_name = "Foydalanuvchi progressi"
        verbose_name_plural = "Foydalanuvchilar progressi"

    def __str__(self):
        return f"{self.user.username} - {self.topic.title} (Max level: {self.highest_level})"