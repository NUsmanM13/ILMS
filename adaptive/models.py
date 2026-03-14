from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='adaptive/courses/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
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
    order = models.PositiveIntegerField(default=0, help_text="Butun kurs bo'ylab dars tartibi (1, 2, 3...)")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.order}. {self.title}"

class Question(models.Model):
    element = models.OneToOneField(Element, on_delete=models.CASCADE, related_name='quiz')
    text = models.CharField(max_length=500)
    option1 = models.CharField(max_length=255)
    option2 = models.CharField(max_length=255)
    option3 = models.CharField(max_length=255)
    option4 = models.CharField(max_length=255)
    correct_option = models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4')])

class Progress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    element = models.ForeignKey(Element, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'element')