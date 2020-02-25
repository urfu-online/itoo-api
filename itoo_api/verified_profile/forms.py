from django import forms
from .models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = '__all__'
        exclude = ['all_valid', 'user', 'diploma_scan']
        terms = forms.BooleanField(required=True)
        widgets = {
            'last_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'required': 'true'
                }
            ),
            'first_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'required': 'true'
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
            'issued_by': forms.TextInput(
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
            'series_diploma': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'number_diploma': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'edu_organization': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'specialty': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'year_of_ending': forms.DateInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            # 'diploma_scan': forms.FileInput(
            #     # attrs={
            #     #     'class': 'form-control'
            #     # }
            # ),

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
        }


class ProfileFormIPMG(forms.ModelForm):
    class Meta:
        model = Profile
        fields = '__all__'
        exclude = ['all_valid', 'user']
        terms = forms.BooleanField(required=True)
        widgets = {
            'last_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'required': 'true'
                }
            ),
            'first_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'required': 'true'
                }
            ),
            'second_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'required': 'true'
                }
            ),
            'sex': forms.Select(
                attrs={
                    'class': 'form-control',
                    'required': 'true'
                }
            ),
            'city': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'required': 'true'
                }
            ),
            'country': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'required': 'true'
                }
            ),
            'birth_date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'required': 'true',
                    'placeholder': 'Год-месяц-день'
                }
            ),
            'birth_place': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'required': 'true'
                }
            ),
            'address_living': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'required': 'true',
                    'placeholder': '620000, г. Екатеринбург, ул. Ленина, дом 140, кв. 154'
                }
            ),

            'job': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'required': 'true',
                    'placeholder': 'Необходимо указать организацию и подразделение'
                }
            ),

            'prefered_org': forms.Select(
                attrs={
                    'class': 'form-control',
                }
            ),

            'position': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'required': 'true'
                }
            ),
            'job_address': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'required': 'true',
                    'placeholder': 'Пример: 620000, г. Екатеринбург, ул. Ленина, дом 140, кв. 154'
                }
            ),

            'phone': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'required': 'true'
                }
            ),
            'add_email': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'required': 'true'
                }
            ),
            'leader_id': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'required': 'true',
                }
            ),
            'SNILS': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'required': 'true',
                }
            ),

            # ПАСПОРТ

            'series': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'required': 'true',
                }
            ),
            'number': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'required': 'true',
                }
            ),
            'issued_by': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'required': 'true',
                    'placeholder': ''
                }
            ),
            'unit_code': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'required': 'true',
                    'placeholder': 'Пример: 123-456'
                }
            ),
            'issue_date': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'required': 'true',
                    'placeholder': 'Пример: 07.02.2000'
                }
            ),
            'address_register': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'required': 'true',
                    'placeholder': '620000, г. Екатеринбург, ул. Ленина, дом 140, кв. 154'
                }
            ),

            # ОБРАЗОВАНИЕ
            'education_level': forms.Select(
                attrs={
                    'class': 'form-control',
                    'required': 'true'
                }
            ),
            'series_diploma': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'required': 'true',
                    'placeholder': 'Пример: 123456'
                }
            ),
            'number_diploma': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'required': 'true',
                    'placeholder': 'Пример: 0012345'
                }
            ),
            'edu_organization': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'required': 'true'
                }
            ),
            'specialty': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'required': 'true'
                }
            ),
            'year_of_ending': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'required': 'true'
                }
            ),
            # 'diploma_scan': forms.FileInput(
            #     # attrs={
            #     #     'class': 'form-control'
            #     # }
            # ),

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

            'all_valid': forms.CheckboxInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            # 'doc_forwarding': forms.FileInput(
            #     attrs={
            #         'class': 'custom-file-input'
            #     }
            # ),
            # 'mail_index': forms.TextInput(
            #     attrs={
            #         'class': 'form-control'
            #     }
            # ),

        }
