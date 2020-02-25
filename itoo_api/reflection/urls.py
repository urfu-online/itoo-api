from django.conf.urls import url, include
from itoo_api.reflection.views import *
from itoo_api.v0.views import CheckSessionID
from rest_framework import routers

router_list = routers.DefaultRouter()
# router_list.register(r'courses_mode_all', CourseModeListAllViewSet)
# router_list.register(r'reflection', ReflectionDetail, base_name="reflection")

app_name = 'reflection'
urlpatterns = [
    # url(r'user_mode_change/', ChangeModeStateUserViewSet.as_view(), name='paid_courses_role'),
    url(r'detail/(?P<pk>\d+)/', AnswerDetail.as_view(), name='reflection_detail'),
    # url(r'pay_urfu/', PayUrfuDataViewSet.as_view(), name='pay_urfu'),
    # url(r'check_session/', CheckSessionID.as_view(), name='check_session'),
    # # url(r'pay_redirect_view/', pay_redirect_view, name='pay_redirect_view'),
    # url(r'offer/(?P<program_slug>\w+)', OfferViewSet.as_view(), name='view_offer'),
    # url(r'paid_course_cus/', PaidCoursesCusViewSet, name='paid_course_cus')
    url(r'', include(router_list.urls)),
]
