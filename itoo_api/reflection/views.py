from django.views.generic import DetailView
from itoo_api.reflection.models import Reflection, Question, Answer
from django import forms
from django.views.generic.edit import FormMixin
from django.http import HttpResponseForbidden
from django.core.urlresolvers import reverse

import logging

logging.basicConfig()
logger = logging.getLogger(__name__)


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


class ReflectionDetail(DetailView, FormMixin):
    model = Reflection
    form_class = AnswerForm
    template_name = '../templates/IPMG/reflection_detail.html'

    def get_success_url(self):
        from django.contrib import messages
        messages.add_message(self.request, messages.INFO, 'form submission success')
        return reverse('reflection_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super(ReflectionDetail, self).get_context_data(**kwargs)
        context['form'] = AnswerForm()
        context['questions'] = Question.objects.filter(reflection=self.get_object())
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        # Here, we would record the user's interest using the message
        # passed in form.cleaned_data['message']
        question = Question.objects.filter(id__exact=self.kwargs['pk'])
        logger.warning(question)
        logger.warning(form.cleaned_data)
        for each in form.cleaned_data['form']:
            logger.warning('****', each, '****', type(each))
            # Answer.objects.create(user=self.request.user, question = question[0])
        return super(ReflectionDetail, self).form_valid(form)


class AnswerDetail(DetailView):
    model = Answer

    def get_context_data(self, **kwargs):
        context = super(AnswerDetail, self).get_context_data(**kwargs)
        context['form'] = AnswerForm()
        context['questions'] = Answer.objects.filter(question=self.get_object())
        context['reflections'] = Answer.objects.filter(
            question=Question.objects.filter(reflection=self.get_object())[0])
        return context
