import requests
from core.config import settings

class GoogleAuthService:
    @staticmethod
    def verify_google_token(id_token: str) -> dict:
        """
        Google ID token'ını doğrular ve kullanıcı bilgilerini döner
        Android için client_secret olmadan çalışır
        """
        # Test modu - gerçek token olmadığında test verisi döner
        if id_token == "test_token":
            return {
                'email': 'test@gmail.com',
                'name': 'Test User',
                'picture': 'https://example.com/test.jpg',
                'sub': 'test_user_id_123',
                'email_verified': True
            }
        
        try:
            # Google'ın token info endpoint'ini kullan (config'den)
            response = requests.get(
                settings.GOOGLE_TOKENINFO_URL,
                params={'id_token': id_token}
            )
            
            if response.status_code != 200:
                raise ValueError('Invalid token')
            
            token_info = response.json()
            
            # Client ID'yi kontrol et
            if token_info.get('aud') != settings.GOOGLE_CLIENT_ID:
                raise ValueError('Wrong audience')
            
            # Token'ın geçerli olup olmadığını kontrol et
            if not token_info.get('email_verified', False):
                raise ValueError('Email not verified')
            
            return {
                'email': token_info.get('email'),
                'name': token_info.get('name', ''),
                'picture': token_info.get('picture', ''),
                'sub': token_info.get('sub'),  # Google user ID
                'email_verified': token_info.get('email_verified', False)
            }
        except Exception as e:
            raise ValueError(f'Token verification failed: {str(e)}')

    @staticmethod
    def get_user_info_from_access_token(access_token: str) -> dict:
        """
        Google access token ile kullanıcı bilgilerini alır
        """
        # Test modu - gerçek token olmadığında test verisi döner
        if access_token == "test_access_token":
            return {
                'email': 'test@gmail.com',
                'name': 'Test User',
                'picture': 'https://example.com/test.jpg',
                'sub': 'test_user_id_123',
                'email_verified': True
            }
        
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            # Google userinfo endpoint'i (config'den)
            response = requests.get(
                settings.GOOGLE_USERINFO_URL,
                headers=headers
            )
            
            if response.status_code == 200:
                user_info = response.json()
                return {
                    'email': user_info.get('email'),
                    'name': user_info.get('name', ''),
                    'picture': user_info.get('picture', ''),
                    'sub': user_info.get('id'),
                    'email_verified': user_info.get('verified_email', False)
                }
            else:
                raise ValueError('Failed to get user info from Google')
        except Exception as e:
            raise ValueError(f'Error getting user info: {str(e)}')

    @staticmethod
    def get_oauth_config() -> dict:
        """
        Google OAuth yapılandırmasını döner
        """
        return {
            'client_id': settings.GOOGLE_CLIENT_ID,
            'project_id': settings.GOOGLE_PROJECT_ID,
            'auth_uri': settings.GOOGLE_AUTH_URI,
            'token_uri': settings.GOOGLE_TOKEN_URI,
            'auth_provider_x509_cert_url': settings.GOOGLE_CERT_URL,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'redirect_uris': [settings.GOOGLE_REDIRECT_URIS],
            'javascript_origins': [settings.GOOGLE_JAVASCRIPT_ORIGINS]
        }
