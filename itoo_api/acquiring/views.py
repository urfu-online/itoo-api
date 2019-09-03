import logging
import json

# rest
from rest_framework.response import Response as RESTResponse, Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.views import APIView
from rest_framework import viewsets, status
# from rest_framework.renderers import TemplateHTMLRenderer

# django
# from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
# from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

# keys course
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey

# models
from course_modes.models import CourseMode
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from itoo_api.models import PayUrfuData

# enroll api
from enrollment import api
# from enrollment.errors import CourseEnrollmentError, CourseEnrollmentExistsError, CourseModeNotFoundError

# serializers
from itoo_api.acquiring.serializers import CourseModeSerializer, ChangeModeStateUserSerializer

logging.basicConfig()
logger = logging.getLogger(__name__)


# acquiring

class CourseModesChange(APIView):
    """
        'mode_slug': u'honor',
        'mode_display_name': u'Honor Code Certificate',
        'min_price': 0,
        'suggested_prices': u'',
        'currency': u'usd',
        'sku': None,
    """

    def get(self, request):
        launch_params = {
            "course_id": request.GET.get('course_id', None),
            "mode_slug": request.GET.get('mode_slug', u'audit'),
            "mode_display_name": request.GET.get('mode_display_name', u'Default display name'),
            "min_price": request.GET.get('min_price', 0),
            "suggested_prices": request.GET.get('suggested_prices', u''),
            "currency": request.GET.get('currency', u'usd'),
            "sku": request.GET.get('sku', None)
        }
        mode_slug = launch_params['mode_slug']
        mode_display_name = launch_params['mode_display_name']
        min_price = launch_params['min_price']
        suggested_prices = launch_params['suggested_prices']
        sku = launch_params['sku']

        course_key_get = launch_params['course_id']
        logger.warning(course_key_get)
        course_key = CourseKey.from_string(course_key_get)
        logger.warning(course_key)
        CourseMode.objects.get_or_create(course_id=course_key, mode_slug=mode_slug, mode_display_name=mode_display_name, min_price=min_price, suggested_prices=suggested_prices, sku=sku)

        return RESTResponse("Mode '{mode_slug}' created for '{course}'.".format(
            mode_slug=launch_params['mode_slug'],
            course=course_key
        ))

class ChangeModeStateUserViewSet(APIView):
    serializer_class = ChangeModeStateUserSerializer

    def get(self, request):
        username = request.GET.get('username')
        course_key = request.GET.get('course_key')
        mode = request.GET.get('mode')
        api.update_enrollment(username, course_key, mode)
        return RESTResponse("Mode '{mode}' on course '{course}' for user {username}.".format(
            mode=mode,
            course=course_key,
            username=username
        ))

    def post(self, request, *args, **kwargs):
        """
        POST /api/itoo_api/v0/paid_courses/
        {
            "user": "Bob"
            "mode": "verified",
            "course_id": "edX/DemoX/Demo_Course",
        }

        """
        serializer = ChangeModeStateUserSerializer(data=request.DATA)
        serializer.is_valid()
        data = serializer.validated_data

        username = data.get('user')
        course_key = data.get('course_key')
        mode = data.get('mode')

        if not course_key:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"message": u"Course ID must be specified to create a new enrollment."}
            )

        try:
            course_key = CourseKey.from_string(course_key)
        except InvalidKeyError:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={
                    "message": u"No course '{course_key}' found for enrollment".format(course_key=course_key)
                }
            )
        try:
            # Lookup the user, instead of using request.user, since request.user may not match the username POSTed.
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            return Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data={
                    'message': u'The user {} does not exist.'.format(username)
                }
            )
        try:
            is_active = data.get('is_active')
            # Check if the requested activation status is None or a Boolean
            if is_active is not None and not isinstance(is_active, bool):
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={
                        'message': (u"'{value}' is an invalid enrollment activation status.").format(value=is_active)
                    }
                )
        except : pass

        enrollment = api.get_enrollment(username, unicode(course_key))
        mode_changed = enrollment and mode is not None and enrollment['mode'] != mode
        active_changed = enrollment and is_active is not None and enrollment['is_active'] != is_active

        if (mode_changed or active_changed):
            if mode_changed and active_changed and not is_active:
                # if the requester wanted to deactivate but specified the wrong mode, fail
                # the request (on the assumption that the requester had outdated information
                # about the currently active enrollment).
                msg = u"Enrollment mode mismatch: active mode={}, requested mode={}. Won't deactivate.".format(
                    enrollment["mode"], mode
                )
                logger.warning(msg)
                return Response(status=status.HTTP_400_BAD_REQUEST, data={"message": msg})

            response = api.update_enrollment(
                username,
                unicode(course_key),
                mode=mode,
                is_active=is_active
            )
        else:
            # Will reactivate inactive enrollments.
            response = api.add_enrollment(
                username,
                unicode(course_key),
                mode=mode,
                is_active=is_active
            )
        return Response(response)


    # def get(self, request, course_id=None):
    #     course_key = CourseKey.from_string(course_id)
    #     course = get_course_by_id(course_key)
    #     return RESTResponse({"course": str(course)})


class CourseModeListAllViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated,IsAdminUser,)

    queryset = CourseOverview.objects.all() # pylint: disable=no-member
    serializer_class = CourseModeSerializer
    lookup_field = 'id'


from django.core import serializers
from django.utils import timezone
from django.utils import six

class PayUrfuDataViewSet(APIView):
    permission_classes = (AllowAny, )

    def post(self, request):
        logger.warning(request.data )
        if request.body == {} or request.body == '-':
            try:
                qd = json.dumps(request.GET, ensure_ascii=False, sort_keys=False)
                obj = PayUrfuData.objects.create(data=qd)
                obj.save()
                return RESTResponse({"Success"})
            except:
                return RESTResponse({"Failed"})
        else:
            obj = PayUrfuData.objects.create(data=request.body)
            obj.save()
            return RESTResponse({"Success"})

    def get(self, request):
        qd = json.dumps(request.GET, ensure_ascii=False, sort_keys=False)
        obj = PayUrfuData.objects.create(data=qd)
        obj.save()
        return RESTResponse({"Success"})