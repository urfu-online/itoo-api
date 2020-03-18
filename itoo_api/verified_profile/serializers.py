import logging

from rest_framework import serializers

from itoo_api.verified_profile.models import Profile, ProfileOrganization
from itoo_api.models import Program
from itoo_api.serializers import ProgramSerializer
from django.http.response import HttpResponseRedirect

logging.basicConfig()
logger = logging.getLogger(__name__)


class ProfileOrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileOrganization
        fields = '__all__'


class ProfileSerializer(serializers.ModelSerializer):
    # groups = GroupSerializer(many=True, read_only=True)
    program = ProgramSerializer(many=False, required=False, read_only=False)
    profile_org = ProfileOrganizationSerializer(many=False, required=False, read_only=False)

    class Meta:
        model = Profile
        fields = '__all__'

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        profile_org_data = validated_data.pop('profile_org')
        return HttpResponseRedirect(redirect_to='...')


class ProfileUNISerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = (
            'last_name',
            'first_name',
            'country',
            "series",
            'number',
            'issue_date',
            'sex',
            'birth_date',
            'address_register'
        )
