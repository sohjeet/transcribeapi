from .authentication import Authenticate ,get_current_active_user, user_is_admin, oauth2_scheme

auth_service = Authenticate()

__all__ = ['auth_service', 'oauth2_scheme', 'get_current_active_user', 'user_is_admin']