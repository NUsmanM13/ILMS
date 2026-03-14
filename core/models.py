from django.db import models

class BotKnowledge(models.Model):
    category = models.CharField(max_length=100, blank=True, verbose_name="Kategoriya (ixtiyoriy)")
    keyword = models.CharField(max_length=255, verbose_name="Kalit so'z yoki termin", help_text="User xabarida shu so'z qatnashsa, javob qaytariladi")
    answer = models.TextField(verbose_name="Bot qaytaradigan javob")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.keyword

    class Meta:
        verbose_name = "Bot bilimi"
        verbose_name_plural = "Bot bilimlari"