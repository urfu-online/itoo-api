# -*- coding: utf-8 -*-
# from itoo_api.verified_profile.data import to_paid_track
from itoo_api.verified_profile.models import Profile
from itoo_api.models import EnrollProgram, Program
from django.contrib.auth.models import User
from opaque_keys.edx.keys import CourseKey
from student.models import CourseEnrollment
from lms.djangoapps.verify_student.models import SoftwareSecurePhotoVerification
import datetime

# paid track
from student.models import CourseEnrollment
from course_modes.models import CourseMode
from openedx.core.djangoapps.course_groups.cohorts import (
    CourseCohort,
    get_course_cohorts,
    is_course_cohorted,
    set_course_cohorted,
    add_user_to_cohort,
    get_cohort,
    get_cohort_by_name
)

from enrollment.api import (
    update_enrollment,
)
from lms.djangoapps.courseware.courses import get_course_by_id
from enrollment.errors import CourseEnrollmentError, CourseEnrollmentExistsError, CourseModeNotFoundError

import logging

logger = logging.getLogger(__name__)

cohorted = True  # Включать когорты


def to_paid_track(userlike_str, course_id, verified_cohort_name="verified", default_cohort_name="default",
                  mode_slug="verified"):
    course_key = CourseKey.from_string(course_id)
    user = User.objects.get(email=userlike_str)
    course = get_course_by_id(course_key)
    acceptable_modes = (
        'verified',
        'professional'
    )

    def _check_user():
        """
        Различные проверки пользовательского аккаунта
        :return: bool
        """
        return user.is_active

    def _check_verified_course_mode():
        course_modes = CourseMode.objects.filter(course_id=course_key, mode_slug__in=acceptable_modes)
        return course_modes

    def _set_user_mode():
        available_verified_modes = _check_verified_course_mode()
        for mode in available_verified_modes:
            if mode.mode_slug == mode_slug:
                update_enrollment(user.username, course_id, mode_slug)
                return True
        return False

        #
        # if not mode:
        #     mode = available_verified_modes[0]
        #
        # if mode in available_verified_modes:
        #     update_enrollment(user.username, course_id, mode)
        # elif mode not in available_verified_modes:
        #     raise CourseModeNotFoundError

    def _get_verified_cohort():
        if not is_course_cohorted(course_key):
            logger.error(
                u"COURSE_NOT_COHORTED: Course '%s' is not cohorted",
                course_id
            )
            set_course_cohorted(course_key, cohorted)

        existing_manual_cohorts = get_course_cohorts(course, assignment_type=CourseCohort.MANUAL)
        logger.info(u"Cohorts on course '%s' '%s'",
                    course_id, existing_manual_cohorts)

        return existing_manual_cohorts[0]
        # if verified_cohort_name:  # алгоритм с одной платной когортой
        #     if not verified_cohort_name in existing_manual_cohorts:
        #         # Создадём когорту и группу контента
        #         cohort = CourseCohort.create(cohort_name=verified_cohort_name, course_id=course_key,
        #                                      assignment_type=CourseCohort.MANUAL)
        #         return cohort
        # else:
        #     """
        #     Место для алгоритма с привязкой когорты к треку и многими треками
        #     """
        #     pass

    def _set_user_cohort():
        cohort = _get_verified_cohort()
        try:
            add_user_to_cohort(cohort, user.username)
        except:
            pass

    def _verify_user():
        if not SoftwareSecurePhotoVerification.user_is_verified(user):
            obj = SoftwareSecurePhotoVerification(user=user, photo_id_key="dummy_photo_id_key")
            obj.status = 'approved'
            obj.submitted_at = datetime.datetime.now()
            obj.reviewing_user = User.objects.get(username='SoftwareSecure')
            obj.save()

    enrollment = None
    try:
        enrollment = CourseEnrollment.get_enrollment(user, course_key)
    except CourseEnrollmentError:
        return "user is not enrolled"

    if enrollment:
        return str(_set_user_mode()), str(_set_user_cohort()), str(_verify_user())

        # def _check_enrollment(self, user, course_key):
        #     enrollment_mode, is_active = CourseEnrollment.enrollment_mode_for_user(user, course_key)
        #
        #     if enrollment_mode is not None and is_active:
        #         all_modes = CourseMode.modes_for_course_dict(course_key, include_expired=True)
        #         course_mode = all_modes.get(enrollment_mode)
        #         has_paid = (course_mode and course_mode.min_price > 0)
        #
        #     return (has_paid, bool(is_active))

        # try:
        enrollment = CourseEnrollment.get_enrollment(user, course_key)
        # Note that this will enroll the user in the default cohort on initial enrollment.
        # That's good because it will force creation of the default cohort if necessary.
        current_cohort = get_cohort(user, course_key)
        verified_cohort = get_cohort_by_name(course_key, verified_cohort_name)


#
# emails = ['anya270993@mail.ru', 'almalah@rambler.ru', 'levakot2004@mail.ru', 'kachalov@tpu.ru',
#           'Bondareva_MA@bsu.edu.ru', 'panich@bsu.edu.ru', 'Ivanova_N-N@mail.ru', 'fomval2011@yandex.ru',
#           'a.s.syrchina@utmn.ru', 'mingal1@pstu.ru', 'irina-taraskina@yandex.ru', 's@mail.ri', 'rublevas@mail.ru',
#           '9502011169@mail.ru', 'elvira.1868@mail.ru', 'mpk46@mail.ru', 'n.d.petriakova@urfu.ru', 'arefevsa@yandex.ru',
#           'Horoshavin.s3@gmail.com', 'Lyusik14@mail.ru', 'yu.lagunova@mail.ru', 'tvp45@mail.ru', 'gpt2004@mail.ru',
#           'VORONOV.1947@mail.ru', 'svamicat@mail.ru', 'o928co@mail.ru', 'airyka@mail.ru', 'mail@kolchina.com',
#           'geodezia_a@mail.ru', 'lyu7660@yandex.ru', 'svetlanabedrina@mail.ru', 'lenta62@mail.ru',
#           'sergey.grebenkin1977@yandex.ru', 'juli.ug@yandex.ru', 'vek-1951@mail.ru', 'fedor_batanin@mail.ru',
#           'andrey-mixal@mail.ru', 'Shestakov.v.s@mail.ru', 'myx660@ya.ru', 'a-idpo@mail.ru', 'dentalia@mail.ru',
#           'alfkaa@mail.ru', 'm.e.kolchina@mail.ru', 'evg0606@mail.ru', '89655066216@mail.ru', 'albert3179@mail.ru',
#           'Ferik1956@mail.ru', 'nikolar07@mail.ru', 'alexgorbunov72@mail.ru', 'ander.stixin.aleks@mail.ru',
#           'legkiyvi@m.usfeu.ru', 'tk.kim@mpgu.edu', 'az_ma@mail.ru', 'natali_savinova@mail.ru', 'sva.eco@gmail.com',
#           '12345AA@mail.ru', 'ivan@mail.ru', 'istorik1981@mail.ru', 'marpoleg@rambler.ru', 'nzoteeva@mail.ru',
#           'kpa57@mail.ru', 'olga.panasyuk/1989@mail.ru', 'melnikalex@list.ru', 'tishemyr@mail.ru', 'alexsm94@gmail.com',
#           'Tatyana_ershowa958@mail.ru', 'vlasov2079@rambler.ru', 'chuhareva0211@mail.ru', '5matroskin@list.ru',
#           'karpov.v@list.ru', 'oxana-komarova@yandex.ru', 'all.be.may@yandex.ru', 'nicolay007@mail.ru',
#           'avl-56@mail.ru', 'ekaterina.podergina@mail.ru', 'egshatkovskaya@gmail.com', 'lyu7660@inbox.ru',
#           'buf@mail.ru', 'o.a.ignatchenko@urfu.ru', 'd.k.satybaldina@urfu.ru', 'nata-malinaa@mail.ru',
#           'marina-lkn@yandex.ru', 'kalexweb@yandex.ru', 'korenkova@bsu.edu.ru', 'malikova@bsu.edu.ru',
#           'bogdanov_d@bsu.edu.ru', 'polyakova_t@bsu.edu.ru', 'e1@mail.ru', 'terekhin@bsu.edu.ru',
#           'ap_chernomaz@student.mpgu.edu', 'vdovin@usfeu.ru', 'i.zashikhina@narfu.ru', '963038@mail.ru',
#           'm.rusinovs@rambler.ru', 'Litvinovandrei-67@mail.ru', 'buharalara@rambler.ru', 'maria070583@mail.ru',
#           'anufrieva@tpu.ru', 'e.hohlushina@narfu.ru', 'r.ovchinnikova@narfu.ru', 'ignatenko_i@bsu.edu.ru',
#           'lev91919@yandex.ru', 'polshchykov@mail.ru', 'n.h.ponetaeva@urfu.ru', '111Kat@mail.ru',
#           'elena.berezova@mail.ru', 'nanish@e1.ru', 'studiotvp@gmail.com', 'legkiyvi@m.usfeu.ru',
#           's.s.kovalchuk@utmn.ru', 'folkdance1@yandex.ru', 'fedortsowa@mail.ru', 'vbelenko@bsu.edu.ru',
#           'kalexweb@yandex.ru', 'snemtsev@bsu.edu.ru', 'e.hohlushina@narfu.ru', 'scuratenko@rambler.ru',
#           'lev91919@yandex.ru', 'yurydubensky@rambler.ru', 'salnikovais@m.usfeu.ru', 'nemzev@bsu.edu.ru',
#           'mamatovav@bsu.edu.ru', 'marinachekameeva@mail.ru', 'syromsvn@mail.ru', 'currently63@yandex.ru',
#           'e.v.patrakov@urfu.ru', 'julia_boltenkova@mail.ru', 's.e.selezneva@urfu.ru', 'irina.iumanova@urfu.ru',
#           's.i.solodushkin@urfu.ru', 'remidosi@gmail.com', 'eco_nataly@mail.ru', 'e.l.gerasimova@urfu.ru',
#           'd.m.spiridonov@urfu.ru', 'spo-1803@yandex.ru', 't.v.shtang@gmail.com', 's.v.mordanov@urfu.ru',
#           'es.gerasimova@yandex.ru', 'tansha2000@mail.ru', 'lenpalna@gmail.com', 'v.v.makarova@urfu.ru',
#           'e.a.buntov@urfu.ru', 'mail-content@mail.ru', 'mvm23@yandex.ru', 'shifrinb@mail.ru', 'n.v.zhelonkin@urfu.ru',
#           's.z.shalygina@urfu.ru', 'n.v.ustinova@urfu.ru', 'Rafael.Sungatullin@kpfu.ru', 'mozgovaya@bsu.edu.ru',
#           'contraste@rambler.ru', 'isosipova@yandex.ru', 'ovsumtsova@tpu.ru', 'kuimova@tpu.ru', 'mactor85@mail.ru',
#           'rymanova@tpu.ru', 'kalexweb@yandex.ru', 'ramsia@inbox.ru', 'mironova@tpu.ru', 'polozova15@tpu.ru',
#           'alya@tpu.ru', 'kulabukhov@bsu.edu.ru', 'kemerovans@tpu.ru', 'kolesnikov@bsu.edu.ru', 'klepikova@bsu.edu.ru',
#           'louise@tpu.ru', 'n.konechnaya@narfu.ru', 'mia2046@yandex.ru', 's.v.masalova@utmn.ru', 'n.v.vojtik@utmn.ru',
#           'MKS-1989eduard@yandex.ru', 'a.zemtsovsky@narfu.ru', 's.m.gercen@utmn.ru', 'allexx1383@mail.ru',
#           'ruslit1611@gmail.com', 'makarovskih@tpu.ru', 'aikina@tpu.ru', 'rd.vnv@rambler.ru',
#           'Chernyavskikh@bsu.edu.ru', 'fokeeva.00@mail.ru', 'alena87@bk.ru', 'lasorokin27@mail.ru',
#           'velichko2005@yandex.ru', 'anufrieva@tpu.ru', 'kernstein@rambler.ru', 'levchaevpa@yandex.ru',
#           'tipnerl@mail.ru', 'stepura@tpu.ru', 'sheveleva@tpu.ru', 'shvagrukova@tpu.ru', 'kozitsina55@mail.ru',
#           'ioannastar@list.ru', 'praw2003@gmail.com', 'osipenko_alexey@mail.ru', 'tedina@yandex.ru',
#           'margeso@yandex.ru', 'lev91919@yandex.ru', 'mityakina@bsu.edu.ru', 'i.m.kalabkina@yandex.ru',
#           'fedoryashenko@bsu.edu.ru', 'e.a.buntov@gmail.com', 'Evgeniia@domain.com', 'akchurinaga@m.usfeu.ru',
#           'abcd123@mail.ru', 'is-1985@yandex.ru', 'e.a.lobanova@utmn.ru', 'Wonder@tpu.ru',
#           'july.shegolikhina@yandex.ru', 'ketrin-star@yandex.ru', 'ea.dernovaia@urfu.ru', 'i.v.erkomaishvili@urfu.ru',
#           'lasina.83@mail.ru', 'pavel@lomasko.com', 'Rusalina2911@rambler.ru', 'tarasovagu@mail.ru', 'shabassv@mail.ru',
#           'an_utkina@mail.ru', 'v.v.egolaev@urfu.ru', 'smostikov@ya.ru', 'eliza.timk@mail.ru', 'tam@imm.uran.ru',
#           '1!@mail.ru', 'optimistka@e1.ru', 'vyazovv@usue.ru', 'oiambusheva@mail.ru', 'om.pliusnina@yandex.ru',
#           'zamaraeva_en@usue.ru', 'irinasavelyeva2008@yandex.ru', '111Kat@mail.ru', 'olya.meshkova@inbox.ru',
#           'alexara@list.ru', 'vis54127@gmail.com', 'popovauni@rambler.ru', 'saharovaev@tpu.ru', 'vaitner@yandex.ru',
#           'teptina.anzhelika@urfu.ru', 'A.G.Galias@urfu.ru', 'VG.Chashchina@urfu.ru', '54aprel@rambler.ru',
#           'a.m.davletshina@urfu.ru', 'i.s.orekhova@urfu.ru', 'stroganov.59@mail.ru', 'poleva_n@list.ru',
#           't.a.pyrkova@urfu.ru', 'aleblinov@yandex.ru', 'a.s.dediukhina@urfu.ru', 'zolinatv@mail.ru',
#           'galiakbar@yande.ru', 'maria.sutormina@urfu.ru', 'nau@hotmail.ru', 'Andrey.Ostrovsky@urfu.ru',
#           'kafedra_ps_urfu@mail.ru', 'dokonechnikov@mail.ru', 'zhdi@inbox.ru', 'iu.a.tokareva@urfu.ru',
#           'massimo2004@mail.ru', 'balabanov-geo@mail.ru', 'eskin.aleksey@gmail.com', 'z.v.shalygina@urfu.ru',
#           'kuv@bk.ru', 'ldanina@yandex.ru', 'bnatalya@mail.ru', 's.v.zimneva@utmn.ru', 'toirinask@gmail.com',
#           'english@tpu.ru', 'andreikorkin@rambler.ru', 'bfog@mail.ru', 'lyudmilatro731@gmail.com',
#           'lyvolkoff@yandex.ru', 'citygirl81@yandex.ru']

#
# users = []
# for username in usernames:
#     users.append(User.objects.get(username=username))
#if EnrollProgram.get_enroll_program(user=user, program=program):
# for user in users:
#     if not SoftwareSecurePhotoVerification.user_is_verified(user):
#         obj = SoftwareSecurePhotoVerification(user=user, photo_id_key="dummy_photo_id_key")
#         obj.status = 'approved'
#         obj.submitted_at = datetime.datetime.now()
#         obj.reviewing_user = User.objects.get(username='SoftwareSecure')
#         obj.save()
#
# users = User.objects.all()
# for user in users:
#     programs = Program.objects.filter(active=True)
#     for program in programs:
#         obj = Profile.get_profile(user=user)
#         if not obj:
#             course_keys = [CourseKey.from_string(course.course_id) for course in program.get_courses()]
#             for course_key in course_keys:
#                 if CourseEnrollment.is_enrolled(user=user, course_key=course_key):
#                     # to_paid_track(user.email, str(course_key))
#                     print user.email, ';', course_key
#
#                     try:
#                         enrollment = CourseEnrollment.objects.get(user=user, course_id=course_key)
#                         enrollment.update_enrollment(is_active=True, mode='verified')
#                     except CourseEnrollment.DoesNotExist:
#                         print(None)

# users = User.objects.all()
