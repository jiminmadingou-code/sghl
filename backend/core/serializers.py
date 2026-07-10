from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        try:
            personnel = user.personnel
            token['role'] = personnel.role
            token['service'] = personnel.service
        except Exception:
            token['role'] = 'Patient'
            token['service'] = ''
        return token

    def validate(self, attrs):
        # Permettre la connexion par email
        username_or_email = attrs.get('username', '')
        if '@' in username_or_email:
            try:
                user = User.objects.get(email=username_or_email.lower())
                attrs['username'] = user.username
            except User.DoesNotExist:
                pass

        data = super().validate(attrs)
        user = self.user

        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': user.get_full_name(),
        }

        try:
            personnel = user.personnel
            user_data['role'] = personnel.role
            user_data['service'] = personnel.service
            user_data['personnel_id'] = personnel.id
        except Exception:
            user_data['role'] = 'Patient'
            user_data['service'] = ''
            user_data['personnel_id'] = None

        data['user'] = user_data
        return data
