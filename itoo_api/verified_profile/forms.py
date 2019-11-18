from django import forms
from .models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = '__all__'
        exclude = ['all_valid', 'user', 'address_register', 'series', 'number', 'issued_by', 'unit_code', 'issue_date', 'passport_scan', 'diploma_scan', 'claim_scan']
        widgets = {
            'last_name': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),
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
            'sex': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),
            'birth_date': forms.DateInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'phone': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'city': forms.TextInput(
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
            # 'address_register': forms.Textarea(
            #     attrs={
            #         'class': 'form-control'
            #     }
            # ),
            # 'claim_scan': forms.FileInput(
            #     # attrs={
            #     #     'class': 'custom-file-input'
            #     # }
            # ),
            'education_level': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),
            'all_valid': forms.CheckboxInput(
                attrs={
                    'class': 'form-control'
                }
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
            'terms': forms.CheckboxInput(
                attrs={
                    'class': 'form-control form-check-input'
                }
            ),
        }
