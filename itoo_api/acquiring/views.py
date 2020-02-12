# -*- coding: utf-8 -*-
import logging
import json
import requests
from datetime import datetime

# rest
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.views import APIView
from rest_framework import viewsets, status
from django.shortcuts import get_object_or_404
# from rest_framework.renderers import TemplateHTMLRenderer

# django
from django.shortcuts import redirect
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
from itoo_api.models import PayUrfuData, Program
from itoo_api.verified_profile.models import Profile

# enroll api
from enrollment import api
from .models import Offer, Payment

# from enrollment.errors import CourseEnrollmentError, CourseEnrollmentExistsError, CourseModeNotFoundError

# serializers
from itoo_api.acquiring.serializers import CourseModeSerializer, ChangeModeStateUserSerializer, OfferSerializer, \
    PaymentSerializer

from .permissions import OwnerPermission

logging.basicConfig()
logger = logging.getLogger(__name__)


# acquiring

class OfferViewSet(APIView):
    permission_classes = (AllowAny,)
    serializer_class = OfferSerializer

    def get(self, request, program_slug):
        # launch_params = {
        #     "program_slug": request.GET.get('program_slug', None),
        # }
        # program_slug = launch_params['program_slug']
        #
        # logger.warning(program_slug)
        offer = Offer.objects.filter(program__slug=program_slug, status='0').first()
        # logger.warning("Found offer: {}".format(offer.title))

        serializer = OfferSerializer(offer)

        return Response(serializer.data)


class CourseModesChange(APIView):
    """
        'mode_slug': u'honor',
        'mode_display_name': u'Honor Code Certificate',
        'min_price': 0,
        'suggested_prices': u'',
        'currency': u'usd',
        'sku': None,
    """
    permission_classes = (AllowAny,)

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
        CourseMode.objects.get_or_create(course_id=course_key, mode_slug=mode_slug, mode_display_name=mode_display_name,
                                         min_price=min_price, suggested_prices=suggested_prices, sku=sku)

        return Response("Mode '{mode_slug}' created for '{course}'.".format(
            mode_slug=launch_params['mode_slug'],
            course=course_key
        ))


class ChangeModeStateUserViewSet(APIView):
    permission_classes = (AllowAny,)

    serializer_class = ChangeModeStateUserSerializer

    def get(self, request):
        username = request.GET.get('username')
        course_key = request.GET.get('course_key')
        mode = request.GET.get('mode')
        api.update_enrollment(username, course_key, mode)
        return Response("Mode '{mode}' on course '{course}' for user {username}.".format(
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
        except:
            pass

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
    #     return Response({"course": str(course)})


class CourseModeListAllViewSet(viewsets.ReadOnlyModelViewSet):
    # permission_classes = (IsAuthenticated,IsAdminUser,)
    permission_classes = (AllowAny,)

    queryset = CourseOverview.objects.all()  # pylint: disable=no-member
    serializer_class = CourseModeSerializer
    lookup_field = 'id'


from django.core import serializers
from django.utils import timezone
from django.utils import six


class PayUrfuDataViewSet(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        # if not request.data:
        #     try:
        #         qd = json.dumps(request.GET, ensure_ascii=False, sort_keys=False)
        #         obj = PayUrfuData.objects.create(data=qd)
        #         obj.save()
        #         return Response({"Success"})
        #     except:
        #         return Response({"Failed": "POST get query params"})
        # else:
        # if not request.GET:
        #     try:
        #         qd = json.dumps(request.GET, ensure_ascii=False, sort_keys=False)
        #         obj = PayUrfuData.objects.create(data='{0}{1}'.format(qd, request.body))
        #         obj.save()
        #         return Response({"Success"})
        #     except:
        #         return Response({"Failed"})
        # else:
        try:
            # qd = json.dumps(request.GET, ensure_ascii=False, sort_keys=False)
            obj = PayUrfuData.objects.create(data=request.body)
            obj.save()
            return Response({"Success"})
        except:
            logger.warning(request.body)
            logger.warning(request.data)
            logger.warning(request.GET)
            return Response({"Failed": "POST body params"})

    def get(self, request):
        qd = json.dumps(request.GET, ensure_ascii=False, sort_keys=False)
        obj = PayUrfuData.objects.create(data=qd)
        obj.save()
        return Response({"Success"})


from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


class PaymentViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = PaymentSerializer
    lookup_field = 'payment_id'

    # @method_decorator(csrf_exempt)
    # def dispatch(self, *args, **kwargs):
    #     return super(PaymentViewSet, self).dispatch(*args, **kwargs)

    def get_permissions(self):
        permission_classes = []
        if self.action == 'create':
            permission_classes = IsAuthenticated

        elif self.action == 'retrieve':
            permission_classes = [OwnerPermission]

        elif self.action == 'list':
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def list(self, request):
        queryset = Payment.objects.all()  # TOD: фильтровать по статусу иои активности
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        offer_id = request.data.get('offer_id', None)
        created = None
        payment = None
        if offer_id:
            # TODO get_or_create or create ???
            # TODO убедиться, что нет активного платежа: user=request.user, offer=Offer.objects.get(pk=offer_id), status != "3"
            # if Payment.objects.get(user=request.user, offer=Offer.objects.get(pk=offer_id)) or Payment.objects.get(
            #         user=request.user, offer=Offer.objects.get(pk=offer_id)).status != "3":
            payment, created = Payment.objects.get_or_create(user=request.user, offer=Offer.objects.get(pk=offer_id))

        if created and payment:
            logger.warn('''Payment created:
                    offer_id: {}
                    payment_id: {}
                    user: {}'''.format(offer_id, str(payment.payment_id), str(request.user)))

            serializer = PaymentSerializer(payment)
            profile = Profile.objects.get(user=request.user)
            offer = Offer.objects.get(pk=offer_id)
            # TODO get all data for payment data
            payment_data = {
                "method": "УрФУ_СервисДоговоры.СохранитьДоговорОферты",
                "params":
                    {
                        "НомерДоговора": "",
                        "ЛСПодразделения": offer.unit_account,
                        "СтатьяДоходов": offer.income_item,
                        "Подразделение": offer.unit,
                        "ИД_Openedurfu": offer.id_urfu,
                        "ДатаРегистрации": request.user.date_joined,
                        "ДатаДоговора": u"{}".format(str(offer.created_at)),
                        "ДатаНачалаДоговора": u"{}".format(str(offer.edu_start_date)),
                        "ДатаОкончанияДоговора": u"{}".format(str(offer.edu_end_date)),
                        "Программа": offer.program.id_unit_program,
                        "ПрограммаНаименование": offer.program.title,
                        "ВидОбразовательнойУслуги": offer.edu_service_type,
                        "Направление": offer.program.direction,
                        "ДатаНачалаПрограммы": u"{}".format(str(offer.program.edu_start_date)),
                        "ДатаОкончанияПрограммы": u"{}".format(str(offer.program.edu_end_date)),
                        "ФормаОбучения": offer.training_form,
                        "СтоимостьОбразовательнойПрограммы": offer.edu_program_cost,
                        "ДатаУстановкиСтоимости": u"{}".format(str(offer.edu_program_cost_date)),
                        "КоличествоЧасов": offer.program.number_of_hours,
                        "ВыдаваемыйДокумент": offer.program.issued_document_name,
                        "Слушатель": {
                            "ФИО": u"{} {} {}".format(profile.last_name, profile.first_name, profile.second_name),
                            "ДатаРождения": profile.birth_date,
                            "Пол": profile.sex,
                            "ИНН": "",
                            "МобильныйТелефон": profile.phone,
                            "Email": request.user.email
                        }
                    }
            }
            logger.warning(payment_data)
            payment_url = 'http://ubu.ustu.ru/buh/hs/ape/rpc'
            payment_request = requests.post(payment_url, data=payment_data, auth=('opened', 'Vra3wb7@'))  # TODO auth ??
            logger.warning('''Response payment: {}'''.format(payment_request))
            response_dicts = json.loads(payment_request.text)
            contract_number = None
            logger.warning("!!!!!!!!!!!!!")
            logger.warning(payment_request.text)
            logger.warning(response_dicts)
            logger.warning(response_dicts.result)
            logger.warning(response_dicts.error)
            for response_dict in response_dicts:
                logger.warning(response_dict)
                if response_dict == "result":
                    contract_number = response_dict['result']['НомерДоговора']
                    payment.status = "1"
                    payment.save()
                    return Response({"status": "sucess", "payment": serializer.data})
                else:
                    contract_number = None
                    payment.status = "3"
                    return Response({"status": "failed"})

            # TODO if payment_request not status error
            # TODO arguments for redirect after receiving payment code
            # TODO payment.status = "1"
            # redirect(
            #     "https://ubu.urfu.ru/pay/?contract_number={}&client_name={}&client_phone={}&client_email={}&amount={}".format())
        else:
            return Response({"status": "failed"})

    # def post(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)
    #     headers = self.get_success_headers(serializer.data)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    #
    # def perform_create(self, serializer):
    #     serializer.save()

    def retrieve(self, request, *args, **kwargs):
        if request.user and request.user.is_authenticated():
            queryset = Payment.objects.filter(user=request.user)
        else:
            queryset = Payment.objects.none()

        logger.warning(self.kwargs['payment_id'])
        payment = get_object_or_404(queryset, payment_id=self.kwargs['payment_id'])
        serializer = PaymentSerializer(payment)
        return Response(serializer.data)
