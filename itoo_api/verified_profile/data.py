from itoo_api.verified_profile.models import Profile
from itoo_api.models import EnrollProgram, Program
from django.contrib.auth.models import User
from opaque_keys.edx.keys import CourseKey
from student.models import CourseEnrollment
from lms.djangoapps.verify_student.models import SoftwareSecurePhotoVerification
import datetime
usernames = [
'Oxana',
'nefedov',
'alexandr_bartysh',
'semenovih',
'Elena-89',
'Anastasia_123',
'alexey_kozhevnikov',
'Bezgina_Julia',
'belovla',
'Alexandra_Margulyan',
'puskarevaolga124',
'Marina_Savsiuk',
'OlgaOrehova',
'Vikharev-Sergey',
'Pyjianov_1957',
'MorozovAE',
'VasiliyA',
'Udintseva',
'sfm9873',
'Tatiana_Lykova',
'Alena_Grigorieva',
'Olga_Karaseva',
'Luidmila',
'Andrey_Morozov',
'Natalia_Skorikova',
'kiselevala',
'Olga_Astafeva',
'vvv',
'Maksim_Ageev',
'svetlana_chelisheva',
'Andrei_Savinovskih',
'galvilag',
'yualia',
]

users = []
for username in usernames:
    users.append(User.objects.get(username=username))

for user in users:
    if not SoftwareSecurePhotoVerification.user_is_verified(user):
        obj = SoftwareSecurePhotoVerification(user=user, photo_id_key="dummy_photo_id_key")
        obj.status = 'approved'
        obj.submitted_at = datetime.datetime.now()
        obj.reviewing_user = User.objects.get(username='SoftwareSecure')
        obj.save()

programs = Program.objects.all()
for program in programs:
    for user in users:
        obj = Profile.get_profile(user=user)
        if obj:
            if EnrollProgram.get_enroll_program(user=user, program=program):
                course_keys = [CourseKey.from_string(course.course_id) for course in program.get_courses()]
                for course_key in course_keys:
                    if CourseEnrollment.is_enrolled(user=user, course_key=course_key):
                        try:
                            enrollment = CourseEnrollment.objects.get(user=user, course_id=course_key)
                            enrollment.update_enrollment(is_active=True, mode='verified')
                        except CourseEnrollment.DoesNotExist:
                            print(None)


# users = User.objects.all()