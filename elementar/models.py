from django.db import models
from django.contrib.auth.models import User

class Lesson(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='lessons/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_progress_percent(self, user):
        from .models import Element, UserProgress
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
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.lesson.title} - {self.title}"

class Element(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='elements')
    title = models.CharField(max_length=255)
    content = models.TextField(help_text="Dars matni (HTML bo'lishi mumkin)")
    video_url = models.URLField(blank=True, null=True, help_text="YouTube video linki")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

class Question(models.Model):
    element = models.OneToOneField(Element, on_delete=models.CASCADE, related_name='quiz')
    text = models.CharField(max_length=500, verbose_name="Test savoli")
    option1 = models.CharField(max_length=255)
    option2 = models.CharField(max_length=255)
    option3 = models.CharField(max_length=255)
    option4 = models.CharField(max_length=255)
    correct_option = models.IntegerField(choices=[(1, '1-variant'), (2, '2-variant'), (3, '3-variant'), (4, '4-variant')])

class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    element = models.ForeignKey(Element, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'element')