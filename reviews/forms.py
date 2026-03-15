from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'body']
        widgets = {
            'rating': forms.RadioSelect(
                choices=[(i, str(i)) for i in range(1, 6)]
            ),
            'body': forms.Textarea(attrs={
                'class': 'bg-gray-800 border border-gray-600 text-white rounded-lg p-3 w-full focus:outline-none focus:ring-2 focus:ring-purple-500 placeholder-gray-400 h-28 resize-none',
                'placeholder': 'اكتب تقييمك هنا...',
            }),
        }