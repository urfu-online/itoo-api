from django.conf.urls import url, include
from itoo_api.reflection.views import *
from itoo_api.v0.views import CheckSessionID
from rest_framework import routers
from django.views.generic import TemplateView
from itoo_api.reflection.views import AnswerViewSet, QuestionViewSet, ReflectionViewSet, ReflectionTemplate

router_list = routers.DefaultRouter()
router_list.register(r'quiz', ReflectionViewSet)
router_list.register(r'answer', AnswerViewSet)
router_list.register(r'question', QuestionViewSet)

app_name = 'reflection'
urlpatterns = [
    # url(r'user_mode_change/', ChangeModeStateUserViewSet.as_view(), name='paid_courses_role'),
    url(r'show/', ReflectionTemplate.as_view(), name='reflection_show'),
    url(r'detail/(?P<pk>\d+)/', ReflectionDetail.as_view(), name='reflection_detail'),
    # url(r'detail/(?P<pk>\d+)/', AnswerDetail.as_view(), name='answer_detail'),
    url(r'success/', TemplateView.as_view(template_name='../templates/IPMG/reflection_success.html'), name='reflection_success'),
    # url(r'pay_urfu/', PayUrfuDataViewSet.as_view(), name='pay_urfu'),
    # url(r'check_session/', CheckSessionID.as_view(), name='check_session'),
    # # url(r'pay_redirect_view/', pay_redirect_view, name='pay_redirect_view'),
    # url(r'offer/(?P<program_slug>\w+)', OfferViewSet.as_view(), name='view_offer'),
    # url(r'paid_course_cus/', PaidCoursesCusViewSet, name='paid_course_cus')
    url(r'', include(router_list.urls)),
]
