from django.db import models
from django.contrib.auth.models import User

class AIPath(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='neural/paths/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_essential_progress(self, user):
        """Faqat muhim elementlar bo'yicha foizni hisoblaydi"""
        from .models import Element, NeuralProgress
        total_essential = Element.objects.filter(module__path=self, is_essential=True).count()
        if total_essential == 0: return 0
        
        completed_essential = NeuralProgress.objects.filter(
            user=user, 
            element__module__path=self, 
            element__is_essential=True, 
            completed=True
        ).count()
        
        return int((completed_essential / total_essential) * 100)

class Module(models.Model):
    path = models.ForeignKey(AIPath, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

class Element(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='elements')
    title = models.CharField(max_length=255)
    content = models.TextField()
    video_url = models.URLField(blank=True, null=True)
    is_essential = models.BooleanField(default=True, verbose_name="Muhim elementmi?") # ASOSIY MANTIQ
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{'[Muhim] ' if self.is_essential else ''}{self.title}"

class Quiz(models.Model):
    element = models.OneToOneField(Element, on_delete=models.CASCADE, related_name='test')
    question = models.CharField(max_length=500)
    option1 = models.CharField(max_length=255)
    option2 = models.CharField(max_length=255)
    option3 = models.CharField(max_length=255)
    option4 = models.CharField(max_length=255)
    correct = models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4')])

class NeuralProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    element = models.ForeignKey(Element, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'element')