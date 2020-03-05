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
AnswerFormSet = inlineformset_factory(Question, Answer, AnswerForm, extra=1)


class ReflectionDetail(CreateView):
    model = Reflection
    form_class = ReflectionForm
    template_name = '../templates/IPMG/reflection_detail.html'

    def get_success_url(self):
        from django.contrib import messages
        messages.add_message(self.request, messages.INFO, 'Ваш ответ успешно записан')
        return reverse('itoo:reflection:reflection_detail', kwargs={'pk': self.object.pk})

    # def get_context_data(self, **kwargs):
    #     context = super(ReflectionDetail, self).get_context_data(**kwargs)
    #     context['answer_form'] = kwargs['answer_form']
    #     return context

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        self.object = None
        form_class = self.get_form_class()
        # form = self.get_form(form_class)
        question_form = QuestionFormSet()
        # question = Question.objects.filter(reflection=self.get_object())
        answer_form = AnswerFormSet()
        logger.warning(answer_form)

        return self.render_to_response(
            self.get_context_data(form=self.get_object(),
                                  answer_form=answer_form, question_form=question_form))

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance and its inline
        formsets with the passed POST variables and then checking them for
        validity.
        """
        self.object = None
        form_class = self.get_form_class()
        # form = self.get_form(form_class)
        answer_form = AnswerFormSet(self.request.POST, request.user)
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
        answer_form.instance.user = self.request.user
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

from rest_framework import viewsets, status
from itoo_api.reflection.serializers import AnswerSerializer, ReflectionSerializer, QuestionSerializer
from itoo_api.reflection.models import Answer, Reflection, Question
from rest_framework.permissions import AllowAny
from itoo_api.verified_profile.permission import IsAdminUser
from rest_framework.response import Response
from django.contrib.auth.models import User


class AnswerViewSet(viewsets.ModelViewSet):
    model = Answer
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    lookup_field = 'id'

    def get_permissions(self):
        permission_classes = []
        if self.action == 'create' or self.action == 'retrieve':
            permission_classes = [AllowAny]
        elif self.action == 'list' or self.action == 'destroy' or self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]


    def create(self, request, *args, **kwargs):
        try:
            for item in request.data:
                question = get_object_or_404(Question, id=item.get('question'))
                user = get_object_or_404(User, username=item.get('username'))
                reflection = get_object_or_404(Reflection, id=item.get('reflection'))
                serializer = self.get_serializer(data=item, many=isinstance(item, list))
                serializer.is_valid(raise_exception=True)
                serializer.save(question=question, user=user, reflection=reflection)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except:
            return Response({'detail': 'Error in AnswerViewSet.create()'}, status=status.HTTP_400_BAD_REQUEST)

class ReflectionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Reflection.objects.all().order_by('id')
    serializer_class = ReflectionSerializer
    lookup_field = 'id'


class QuestionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Question.objects.all().order_by('id')
    serializer_class = QuestionSerializer
    lookup_field = 'id'
