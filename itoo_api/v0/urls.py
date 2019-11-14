"""
URLS for itoo_api end points.
"""
# pylint: disable=invalid-name (?P<slug>\w+)/$
from rest_framework import routers

from itoo_api.v0.views import ProgramViewSet, ProgramCourseViewSet, \
    OrganizationCustomViewSet, OrganizationCourseViewSet, EduProjectViewSet, ProfileViewSet, EnrollProgramViewSet

router = routers.SimpleRouter()
router.register(r'projects', EduProjectViewSet)
router.register(r'programs', ProgramViewSet)
router.register(r'link_courses_program', ProgramCourseViewSet)
router.register(r'organizations', OrganizationCustomViewSet)
router.register(r'link_courses_org', OrganizationCourseViewSet)
router.register(r'valid', ProfileViewSet)
router.register(r'enroll_program', EnrollProgramViewSet)
# router.register(r'paid_courses_role', PaidCoursesRoleViewSet.as_view(), base_name='paid_courses_role')
# router.register(r'add_enroll/(?P<user_id>\d+)&(?P<course_id>\d+)&(?P<mode>\d+)/?$', AddEnrollmentViewSet, base_name='add_enroll')

app_name = 'v0'
urlpatterns = router.urls
