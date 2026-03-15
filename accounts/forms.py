from django import forms
from .models import User

STYLE = 'bg-gray-700 border border-gray-600 text-white rounded-lg px-4 py-2 w-full focus:outline-none focus:ring-2 focus:ring-purple-500 placeholder-gray-400'
TEXTAREA = 'bg-gray-700 border border-gray-600 text-white rounded-lg px-4 py-2 w-full focus:outline-none focus:ring-2 focus:ring-purple-500 placeholder-gray-400 h-32 resize-none'
FILE = 'block w-full text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-purple-600 file:text-white hover:file:bg-purple-700 cursor-pointer'


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['avatar', 'bio', 'first_name', 'last_name']
        widgets = {
            'avatar': forms.FileInput(attrs={'class': FILE}),
            'bio': forms.Textarea(attrs={'class': TEXTAREA, 'placeholder': 'اكتب نبذة عنك...'}),
            'first_name': forms.TextInput(attrs={'class': STYLE, 'placeholder': 'الاسم الأول'}),
            'last_name': forms.TextInput(attrs={'class': STYLE, 'placeholder': 'اسم العائلة'}),
        }