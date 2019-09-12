from django import forms
from .models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = '__all__'
        exclude = ['all_valid']
        widgets = {
            'first_name': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'last_name': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'second_name': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'sex': forms.Select(
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
            'job': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'position': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'address_register': forms.Textarea(
                attrs={
                    'class': 'form-control'
                }
            ),
            'claim_scan': forms.FileInput(
                # attrs={
                #     'class': 'custom-file-input'
                # }
            ),
            'series': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'number': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'issued_by': forms.Textarea(
                attrs={
                    'class': 'form-control'
                }
            ),
            'unit_code': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'issue_date': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'passport_scan': forms.FileInput(
                # attrs={
                #     'class': 'custom-file-input'
                # }
            ),
            'education_level': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'diploma_scan': forms.FileInput(
                # attrs={
                #     'class': 'custom-file-input'
                # }
            ),
            'doc_forwarding': forms.FileInput(
                # attrs={
                #     'class': 'custom-file-input'
                # }
            ),
            'mail_index': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'country': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'address_living': forms.Textarea(
                attrs={
                    'class': 'form-control'
                }
            ),
        }
