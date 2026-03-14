from django.db import models
from django.contrib.auth.models import User

class Subject(models.Model):
    name = models.CharField(max_length=255, verbose_name="Fan nomi")
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Question(models.Model):
    LEVEL_CHOICES = [(3, '3 baholik'), (4, '4 baholik'), (5, '5 baholik')]
    
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField(verbose_name="Savol matni")
    option1 = models.CharField(max_length=255)
    option2 = models.CharField(max_length=255)
    option3 = models.CharField(max_length=255)
    option4 = models.CharField(max_length=255)
    correct_option = models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4')])
    
    # Adaptive test uchun
    level = models.IntegerField(choices=LEVEL_CHOICES, default=3)
    
    # Koeffitsiyentli test uchun
    coefficient = models.FloatField(default=1.0, verbose_name="Koeffitsiyent (Ball)")

    def __str__(self):
        return f"{self.subject.name} - {self.text[:50]}"

class ExamSession(models.Model):
    TYPE_CHOICES = [('simple', 'Oddiy'), ('adaptive', 'Adaptive'), ('coefficient', 'Koeffitsiyentli')]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    exam_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    
    started_at = models.DateTimeField(auto_now_add=True)
    is_finished = models.BooleanField(default=False)
    
    # Natijalar
    total_questions = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    score = models.FloatField(default=0.0) # Foiz yoki ball
    final_grade = models.IntegerField(null=True, blank=True) # Adaptive uchun (3,4,5)

    def __str__(self):
        return f"{self.user.username} - {self.exam_type}"