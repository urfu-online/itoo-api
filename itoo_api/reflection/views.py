from django.views.generic import DetailView
from itoo_api.reflection.models import Reflection, Question, Answer
from django import forms
from django.views.generic.edit import FormMixin


class ReflectionDetail(DetailView):
    model = Reflection
    template_name = '../templates/IPMG/reflection_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ReflectionDetail, self).get_context_data(**kwargs)
        context['form'] = AnswerForm()
        context['questions'] = Question.objects.filter(reflection=self.get_object())
        return context


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = '__all__'
        widgets = {
            'answer_text': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'required': 'true'
                }
            ),
            'answer_float': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'required': 'true'
                }
            ),
        }


class AnswerDetail(DetailView):
    model = Answer

    def get_context_data(self, **kwargs):
        context = super(AnswerDetail, self).get_context_data(**kwargs)
        context['form'] = AnswerForm()
        context['questions'] = Answer.objects.filter(question=self.get_object())
        context['reflections'] = Answer.objects.filter(
            question=Question.objects.filter(reflection=self.get_object())[0])
        return context
