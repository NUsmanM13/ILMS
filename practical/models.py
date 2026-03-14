from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

class Assignment(models.Model):
    TYPE_CHOICES = [('practical', 'Amaliy mashg’ulot'), ('independent', 'Mustaqil ta’lim')]
    
    title = models.CharField(max_length=255, verbose_name="Topshiriq nomi")
    task_type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Turi")
    description = models.TextField(verbose_name="Topshiriq tavsifi")
    file = models.FileField(upload_to='assignments/tasks/', verbose_name="Topshiriq fayli (PDF/Word)")
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField(verbose_name="Topshiriq muddati", null=True, blank=True)

    def __str__(self):
        return f"{self.get_task_type_display()}: {self.title}"

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='practical_submissions')
    file = models.FileField(upload_to='assignments/submissions/', verbose_name="Talaba javob fayli")
    comment = models.TextField(blank=True, verbose_name="Talaba izohi")
    
    # Baholash qismi
    grade = models.PositiveIntegerField(
        null=True, blank=True, 
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Baho (0-100)"
    )
    teacher_comment = models.TextField(blank=True, verbose_name="O'qituvchi taqrizi")
    graded_at = models.DateTimeField(null=True, blank=True)
    is_graded = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('assignment', 'user') # Bir talaba bir topshiriqqa bir marta javob beradi

    def __str__(self):
        return f"{self.user.username} - {self.assignment.title}"