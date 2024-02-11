import pytest
from app import settings
from jose import jwt, JWTError
from unittest.mock import patch, MagicMock
from pydantic import ValidationError
from users.schemas import  JWTPayload, TokenData

@pytest.mark.usefixtures('auth_obj')
@pytest.mark.usefixtures('dummy_user')
class TestAuthenticate:

    ''' Test the create_hashed_password method of the auth_service'''
    def test_create_hashed_password(self, auth_obj):
        test_password = '123456789'
        first_password = auth_obj.create_hashed_password(plaintext_password=test_password)
        second_password = auth_obj.create_hashed_password(plaintext_password=test_password)
        assert first_password is not second_password

    ''' Test the verify_password method of the auth_service'''
    def test_create_access_token(self, auth_obj, dummy_user):
        token = auth_obj.create_access_token(user=dummy_user)
        decoded = jwt.decode(token,
                            str(settings.SECRET_KEY),
                            audience=settings.JWT_AUDIENCE,
                            algorithms=settings.JWT_ALGORITHM)
        assert isinstance(decoded, dict)
        assert decoded['username'] == dummy_user.username

    ''' Test the create_access_token method of the auth_service with wrong secret key, audience and algorithm'''
    def test_create_access_token_for_user_wrong_secret_key(self, auth_obj, dummy_user):
        token = auth_obj.create_access_token(user=dummy_user)
        with pytest.raises(JWTError) as jwt_error:
            jwt.decode(
                token,
                str('nice-wrong-secret-key'),
                audience=settings.JWT_AUDIENCE,
                algorithms=settings.JWT_ALGORITHM
            )

        assert 'Signature verification failed' in str(jwt_error.value)

    def test_create_access_token_for_user_wrong_audience(self, auth_obj, dummy_user):
        token = auth_obj.create_access_token(user=dummy_user)
        with pytest.raises(JWTError) as jwt_error:
            jwt.decode(token,
                        str(settings.SECRET_KEY),
                        audience='heyyy',
                        algorithms=settings.JWT_ALGORITHM)

        assert 'Invalid audience' in str(jwt_error.value)

    def test_create_access_token_for_user_wrong_algo(self, auth_obj, dummy_user):
        token = auth_obj.create_access_token(user=dummy_user)
        with pytest.raises(JWTError) as jwt_error:
            jwt.decode(token,
                        str(settings.SECRET_KEY),
                        audience=settings.JWT_AUDIENCE,
                        algorithms='HMAC')

        assert 'The specified alg value is not allowed' in str(jwt_error.value)

    def test_create_access_token_for_user_no_user(self, auth_obj):
        token = auth_obj.create_access_token(user=None)
        assert token is None

    def test_verify_password(self, auth_obj, dummy_user):
        is_verified = auth_obj.verify_password(password='dummyuserswesomepass',
                                            hashed_pw=dummy_user.password)
        assert is_verified is True
