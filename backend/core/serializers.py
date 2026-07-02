from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        try:
            personnel = user.personnel
            token['role'] = personnel.role
            token['service'] = personnel.service
        except Exception:
            token['role'] = 'User'
            token['service'] = ''
        return token

    def validate(self, attrs):
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
            user_data['role'] = 'User'
            user_data['service'] = ''
            user_data['personnel_id'] = None
            
        data['user'] = user_data
        return data
