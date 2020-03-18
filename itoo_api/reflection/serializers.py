import logging
from rest_framework import serializers

from itoo_api.reflection.models import Reflection, Question, Answer
from itoo_api.serializers import ProgramSerializer

from django.contrib.auth.models import User
from openedx.core.djangoapps.user_api.serializers import UserSerializer
from rest_framework.response import Response

logging.basicConfig()
logger = logging.getLogger(__name__)


class ReflectionSerializer(serializers.ModelSerializer):
    # program = ProgramSerializer(source='program.slug')
    program_slug = serializers.CharField(source='program.slug', read_only=True)

    class Meta:
        model = Reflection
        fields = ['id', 'title', 'description', 'program_slug']


class QuestionSerializer(serializers.ModelSerializer):
    reflection = ReflectionSerializer(many=False, required=False, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'title', 'reflection']


class AnswerSerializer(serializers.ModelSerializer):
    # def __init__(self, *args, **kwargs):
    #     many = kwargs.pop('many', True)
    #     super(AnswerSerializer, self).__init__(many=many, *args, **kwargs)

    question = QuestionSerializer(source='question.id', many=False, read_only=True)
    username = UserSerializer(source="user.username", read_only=True, required=False)
    reflection = ReflectionSerializer(source='reflection.id', many=False, required=False, read_only=True)

    class Meta:
        model = Answer
        fields = ['answer_text', 'answer_float', 'username', 'question', 'reflection']
