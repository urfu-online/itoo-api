import logging
from rest_framework import serializers

from itoo_api.reflection.models import Reflection, Question, Answer
from itoo_api.serializers import ProgramSerializer

from django.contrib.auth.models import User
from rest_framework.response import Response

logging.basicConfig()
logger = logging.getLogger(__name__)


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'title']


class ReflectionSerializer(serializers.ModelSerializer):
    program_slug = ProgramSerializer(read_only=True, source='program.program_slug')
    question = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Reflection
        fields = ['id', 'title', 'description', 'program_slug', 'question']


class AnswerSerializer(serializers.ModelSerializer):
    question = QuestionSerializer(many=False, required=True)
    reflection = ReflectionSerializer(many=False, required=False, source='reflection.pk')

    class Meta:
        model = Answer
        fields = ['answer_text', 'answer_float', 'username', 'question', 'reflection']

    def create(self, validated_data):
        answer_data = validated_data.pop('answer')
        if User.objects.get(user=self.request.user) and Reflection.objects.get(
                id=answer_data['reflection']) and Question.objects.get(id=answer_data['question']):
            user = User.objects.get(user=self.request.user)
            answer = Answer.objects.create(user=user, **answer_data)
            return answer
        else:
            return Response({'detail': 'failed'})
