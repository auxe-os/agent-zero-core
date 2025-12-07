from python.helpers import dotenv
import hashlib


def get_credentials_hash():
    """Gets the SHA256 hash of the user's credentials.

    Returns:
        The SHA256 hash of the user's credentials, or None if no user is
        configured.
    """
    user = dotenv.get_dotenv_value("AUTH_LOGIN")
    password = dotenv.get_dotenv_value("AUTH_PASSWORD")
    if not user:
        return None
    return hashlib.sha256(f"{user}:{password}".encode()).hexdigest()


def is_login_required():
    """Checks if login is required.

    Returns:
        True if login is required, False otherwise.
    """
    user = dotenv.get_dotenv_value("AUTH_LOGIN")
    return bool(user)
