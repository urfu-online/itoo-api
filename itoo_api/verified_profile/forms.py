from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = '__all__'
        widgets = {
            'first_name': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'second_name': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'city': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'birth_date': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'phone': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),
        }