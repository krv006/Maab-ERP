from django.contrib.auth.hashers import make_password
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField, EmailField
from rest_framework.serializers import ModelSerializer, Serializer

from users.models import User, StudentJourney, Language


class RegisterUserModelSerializer(ModelSerializer):
    confirm_password = CharField(write_only=True)

    class Meta:
        model = User
        fields = 'id', 'email', 'password', 'confirm_password',

        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, attrs):
        confirm_password = attrs.pop('confirm_password')
        if confirm_password != attrs.get('password'):
            raise ValidationError('Passwords did not match!')
        attrs['password'] = make_password(confirm_password)
        return attrs


class LoginUserModelSerializer(Serializer):
    email = EmailField()
    password = CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValidationError("Invalid email or password")

        if not user.check_password(password):
            raise ValidationError("Invalid email or password")
        if not user.is_active:
            user.is_active = True
            user.save(update_fields=['is_active'])
        attrs['user'] = user
        return attrs


class UserModelSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class UserRoleUpdateModelSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = 'id', 'role',


class StudentJourneyModelSerializer(ModelSerializer):
    class Meta:
        model = StudentJourney
        fields = '__all__'

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['user'] = UserModelSerializer(instance.user).data if instance.user else None
        return repr


class StudentJourneyInJobModelSerializer(ModelSerializer):
    class Meta:
        model = StudentJourney
        fields = 'id', 'job_offer_accepted',


class StudentJourneyStatusUpdateModelSerializer(ModelSerializer):
    class Meta:
        model = StudentJourney
        fields = 'id', 'status',


class LanguageModelSerializer(ModelSerializer):
    class Meta:
        model = Language
        fields = 'id', 'language', 'language_grid', 'user',

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['user'] = UserModelSerializer(instance.user).data if instance.user else None
        return repr
