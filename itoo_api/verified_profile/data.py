# -*- coding: utf-8 -*-
from itoo_api.verified_profile.models import Profile
from itoo_api.models import EnrollProgram, Program
from django.contrib.auth.models import User
from opaque_keys.edx.keys import CourseKey
import logging
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

logger = logging.getLogger(__name__)

cohorted = True  # Включать когорты


def to_paid_track(userlike_str, course_id, verified_cohort_name=None, default_cohort_name="default", mode=None):
    course_key = CourseKey.from_string(course_id)
    user = User.objects.get(email=userlike_str)
    course = get_course_by_id(course_id)
    acceptable_modes = (
        'verified'
        'professional'
    )

    def _check_user():
        """
        Различные проверки пользовательского аккаунта
        :return: bool
        """
        return user.is_active

    def _check_verified_course_mode():
        modes_dict = CourseMode.modes_for_course_dict(
            course_id=course_id,
            modes=acceptable_modes,
            include_expired=False,
            course=course
        )
        available_verified_modes = []
        course_modes = CourseMode.objects.filter(course_id=course_id)
        for mode in course_modes:
            available_verified_modes.append(modes_dict.get(mode, None))
        return available_verified_modes

    def _get_verified_cohort():
        if not is_course_cohorted(course_key):
            logger.error(
                u"COURSE_NOT_COHORTED: Course '%s' is not cohorted",
                course_id
            )
            set_course_cohorted(course_key, cohorted)

        logger.warning(course_key)
        course = get_course_by_id(course_key)
        existing_manual_cohorts = get_course_cohorts(course, assignment_type=CourseCohort.MANUAL)
        logger.info(u"Cohorts on course '%s' '%s'",
                    course_id, existing_manual_cohorts)
        if verified_cohort_name:  # алгоритм с одной платной когортой
            if not verified_cohort_name in existing_manual_cohorts:
                # Создадём когорту и группу контента
                cohort = CourseCohort.create(cohort_name=verified_cohort_name, course_id=course_id,
                                             assignment_type=CourseCohort.MANUAL)
                return cohort
        else:
            """
            Место для алгоритма с привязкой когорты к треку и многими треками
            """
            pass

    def _set_user_mode():
        available_verified_modes = _check_verified_course_mode()

        if not mode:
            mode = available_verified_modes[0]

            if mode in available_verified_modes:
                update_enrollment(user.username, course_key, mode)
            elif mode not in available_verified_modes:
                raise CourseModeNotFoundError

    def _set_user_cohort():
        cohort = _get_verified_cohort()
        add_user_to_cohort(cohort, user.email)

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
# usernames = [
# 'Oxana',
# 'nefedov',
# 'alexandr_bartysh',
# 'semenovih',
# 'Elena-89',
# 'Anastasia_123',
# 'alexey_kozhevnikov',
# 'Bezgina_Julia',
# 'belovla',
# 'Alexandra_Margulyan',
# 'puskarevaolga124',
# 'Marina_Savsiuk',
# 'OlgaOrehova',
# 'Vikharev-Sergey',
# 'Pyjianov_1957',
# 'MorozovAE',
# 'VasiliyA',
# 'Udintseva',
# 'sfm9873',
# 'Tatiana_Lykova',
# 'Alena_Grigorieva',
# 'Olga_Karaseva',
# 'Luidmila',
# 'Andrey_Morozov',
# 'Natalia_Skorikova',
# 'kiselevala',
# 'Olga_Astafeva',
# 'vvv',
# 'Maksim_Ageev',
# 'svetlana_chelisheva',
# 'Andrei_Savinovskih',
# 'galvilag',
# 'yualia',
# ]
#
# users = []
# for username in usernames:
#     users.append(User.objects.get(username=username))
#
# for user in users:
#     if not SoftwareSecurePhotoVerification.user_is_verified(user):
#         obj = SoftwareSecurePhotoVerification(user=user, photo_id_key="dummy_photo_id_key")
#         obj.status = 'approved'
#         obj.submitted_at = datetime.datetime.now()
#         obj.reviewing_user = User.objects.get(username='SoftwareSecure')
#         obj.save()
#
# programs = Program.objects.all()
# for program in programs:
#     for user in users:
#         obj = Profile.get_profile(user=user)
#         if obj:
#             if EnrollProgram.get_enroll_program(user=user, program=program):
#                 course_keys = [CourseKey.from_string(course.course_id) for course in program.get_courses()]
#                 for course_key in course_keys:
#                     if CourseEnrollment.is_enrolled(user=user, course_key=course_key):
#                         try:
#                             enrollment = CourseEnrollment.objects.get(user=user, course_id=course_key)
#                             enrollment.update_enrollment(is_active=True, mode='verified')
#                         except CourseEnrollment.DoesNotExist:
#                             print(None)


# users = User.objects.all()
