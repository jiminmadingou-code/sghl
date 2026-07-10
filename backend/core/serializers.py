from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth.models import User


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        try:
            token['role'] = user.personnel.role
            token['service'] = user.personnel.service
        except Exception:
            token['role'] = 'Patient'
            token['service'] = ''
        return token

    def validate(self, attrs):
        # Accepter email OU username dans le champ username
        username_or_email = attrs.get('username', '').strip()
        if '@' in username_or_email:
            try:
                user = User.objects.get(email=username_or_email.lower())
                attrs['username'] = user.username
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    {'detail': 'Aucun compte trouvé avec cet email.'}
                )

        data = super().validate(attrs)
        user = self.user

        role = 'Patient'
        service = ''
        personnel_id = None
        try:
            role = user.personnel.role
            service = user.personnel.service
            personnel_id = user.personnel.id
        except Exception:
            pass

        data['user'] = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': user.get_full_name() or user.username,
            'role': role,
            'service': service,
            'personnel_id': personnel_id,
        }
        return data
