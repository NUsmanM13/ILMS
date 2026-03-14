from django.db import models
from django.contrib.auth.models import User

class Folder(models.Model):
    name = models.CharField(max_length=255, verbose_name="Mavzu nomi")
    description = models.TextField(blank=True, verbose_name="Mavzu haqida")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Material(models.Model):
    """Admin yuklaydigan darsliklar va vazifalar"""
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='materials')
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='materials/%Y/%m/')
    is_assignment = models.BooleanField(default=False, verbose_name="Bu uyga vazifami?")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Submission(models.Model):
    """Talaba topshiradigan uyga vazifa javobi"""
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='submissions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='submissions/%Y/%m/')
    comment = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.folder.name}"