import logging
from rest_framework import serializers

from itoo_api.reflection.models import Reflection, Question, Answer
from itoo_api.serializers import ProgramSerializer

from django.contrib.auth.models import User
from rest_framework.response import Response

logging.basicConfig()
logger = logging.getLogger(__name__)


class ReflectionSerializer(serializers.ModelSerializer):
    # program = ProgramSerializer(source='program.slug')
    program_slug = serializers.CharField(source='program.slug')

    class Meta:
        model = Reflection
        fields = ['id', 'title', 'description', 'program_slug']


class QuestionSerializer(serializers.ModelSerializer):
    reflection = ReflectionSerializer(many=False, required=False)

    class Meta:
        model = Question
        fields = ['id', 'title', 'reflection']


class AnswerSerializer(serializers.ModelSerializer):
    question = QuestionSerializer(many=False, read_only=True)
    # reflection = ReflectionSerializer(many=False, required=False)
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Answer
        fields = ['answer_text', 'answer_float', 'username', 'question']
        # answer_data = validated_data.pop('answer')
        # try:
        #     for obj in answer_data['question']:
        #         logger.warning(obj)
        #     User.objects.get(username=answer_data['username']) and Reflection.objects.get(
        #         id=answer_data['reflection']) and Question.objects.get(id=answer_data['question'])
        #     user = User.objects.get(username=answer_data['username'])
        #     if User.objects.get(username=answer_data['username']) and Reflection.objects.get(
        #             id=answer_data['reflection']) and Question.objects.get(id=answer_data['question']):
        #         answer = Answer.objects.create(user=user, **answer_data)
        #         return answer
        #     else:
        #         Response({'detail': 'failed'})
        # except:
        #     return Response({'detail': 'failed'})
