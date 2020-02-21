from django.views.generic import DetailView
from itoo_api.reflection.models import Reflection, Question


class ReflectionDetail(DetailView):
    model = Reflection

    def get_context_data(self, **kwargs):
        context = super(ReflectionDetail, self).get_context_data(**kwargs)
        context['questions'] = Question.objects.filter(reflection=self.get_object())
        return context
