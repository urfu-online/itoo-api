# -*- coding: utf-8 -*-
from django.contrib import admin
from itoo_api.reflection.models import Reflection, Question, Answer


class QuestionInline(admin.TabularInline):
    model = Question


@admin.register(Reflection)
class ReflectionAdmin(admin.ModelAdmin):
    model = Reflection
    list_display = ('title', 'description', 'program',)
    list_filter = ('program',)
    search_fields = ('title', 'program',)
    inlines = [QuestionInline, ]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    model = Answer
    list_display = ('user__email', 'question',)
    search_fields = ('user__email', 'user__username')
