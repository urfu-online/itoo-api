# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, CreateView
from itoo_api.reflection.models import Reflection, Question, Answer
from django import forms
from django.views.generic.edit import FormMixin
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.forms.models import inlineformset_factory

import logging

logging.basicConfig()
logger = logging.getLogger(__name__)


class ReflectionForm(forms.ModelForm):
    class Meta:
        model = Reflection
        fields = '__all__'
        exclude = ('program',)


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ('order',)


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


QuestionFormSet = inlineformset_factory(Reflection, Question, QuestionForm)
AnswerFormSet = inlineformset_factory(Reflection, Answer, AnswerForm)


class ReflectionDetail(CreateView):
    model = Reflection
    form_class = ReflectionForm
    template_name = '../templates/IPMG/reflection_detail.html'

    def get_success_url(self):
        from django.contrib import messages
        messages.add_message(self.request, messages.INFO, 'Ваш ответ успешно записан')
        return reverse('itoo:reflection:reflection_detail', kwargs={'pk': self.object.pk})

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        self.object = None
        form_class = self.get_form_class()
        # form = self.get_form(form_class)
        # question_form = QuestionFormSet()
        answer_form = AnswerFormSet()
        return self.render_to_response(
            self.get_context_data(form=self.get_object(),
                                  answer_form=answer_form))

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance and its inline
        formsets with the passed POST variables and then checking them for
        validity.
        """
        self.object = None
        form_class = self.get_form_class()
        # form = self.get_form(form_class)
        answer_form = AnswerFormSet(self.request.POST)
        if (answer_form.is_valid()):
            return self.form_valid(answer_form)
        else:
            return self.form_invalid(answer_form)

    def form_valid(self, answer_form):
        """
        Called if all forms are valid. Creates a Recipe instance along with
        associated Ingredients and Instructions and then redirects to a
        success page.
        """
        answer_form.instance = self.object
        answer_form.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, answer_form):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """
        return self.render_to_response(
            self.get_context_data(answer_form=answer_form))

# class AnswerDetail(DetailView, FormMixin):
#     model = Answer
#     template_name = '../templates/IPMG/reflection_detail.html'
#
#     def get_success_url(self):
#         from django.contrib import messages
#         messages.add_message(self.request, messages.INFO, 'Ваш ответ успешно записан')
#         return reverse('itoo:reflection:answer_detail', kwargs={'pk': self.object.pk})
#
#     def get_context_data(self, **kwargs):
#         context = super(AnswerDetail, self).get_context_data(**kwargs)
#         context['form'] = AnswerForm()
#         context['questions'] = Answer.objects.filter(question=self.get_object())
#         context['reflections'] = Answer.objects.filter(
#             question=Question.objects.filter(reflection=self.get_object())[0])
#         return context
#
#     def post(self, request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return HttpResponseForbidden()
#         self.object = self.get_object()
#         form = self.get_form()
#         logger.warning(form)
#         if form.is_valid():
#             return self.form_valid(form)
#         else:
#             return self.form_invalid(form)
#
#     def form_valid(self, form):
#         # Here, we would record the user's interest using the message
#         # passed in form.cleaned_data['message']
#         question = Question.objects.filter(reflection=self.get_object())
#         logger.warning('!!!!!!!!!!!!!!!!')
#         logger.warning(form.cleaned_data['answer_text'])
#         logger.warning(question)
#         logger.warning(type(question))
#         for obj in question:
#             for each in form.cleaned_data['answer_text']:
#                 # logger.warning('****', each, '****', type(each))
#
#                 Answer.objects.create(user=self.request.user, question=obj, answer_text=each)
#         return super(AnswerDetail, self).form_valid(form)
