from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class UzbekUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username",)
        labels = {
            'username': "Foydalanuvchi nomi",
        }
        help_texts = {
            'username': "Harflar, raqamlar va @/./+/-/_ belgilari.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Parol maydonlarini o'zbekcha qilish
        self.fields['password1'].label = "Parol"
        self.fields['password2'].label = "Parolni tasdiqlash"
        self.fields['password1'].help_text = "Parolingiz juda oddiy bo'lmasligi kerak."
        self.fields['password2'].help_text = "Tasdiqlash uchun parolni qayta kiriting."