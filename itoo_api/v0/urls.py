"""
URLS for itoo_api end points.
"""
# pylint: disable=invalid-name (?P<slug>\w+)/$
from rest_framework import routers
from django.conf import settings

from course_modes.models import CourseMode

from itoo_api.v0.views import ProgramViewSet, OrganizationViewSet, ProgramCourseViewSet, EnrollmentViewSet, \
    OrganizationCustomViewSet, OrganizationCourseViewSet, PaidCoursesViewSet, PaidCoursesViewSet2

router = routers.SimpleRouter()
router.register(r'programs', ProgramViewSet)
router.register(r'link_courses_program', ProgramCourseViewSet)
router.register(r'organizations', OrganizationCustomViewSet)
router.register(r'link_courses_org', OrganizationCourseViewSet)
router.register(r'paid_course', PaidCoursesViewSet2)
router.register(r'enrollment/{username},{course_key}$'.format(
    username=settings.USERNAME_PATTERN, course_key=settings.COURSE_ID_PATTERN
),
    EnrollmentViewSet, base_name='enrollment')

router.register(r'paid_courses/{course_key}', PaidCoursesViewSet, base_name=CourseMode)

app_name = 'v0'
urlpatterns = router.urls
