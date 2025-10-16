from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Dict

try:
    import requests  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    requests = None  # type: ignore

from django.conf import settings

try:
    from google.auth.transport import requests as google_requests  # type: ignore
    from google.oauth2 import id_token as google_id_token  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    google_requests = None  # type: ignore
    google_id_token = None  # type: ignore

try:
    import jwt  # type: ignore
    from jwt.algorithms import RSAAlgorithm  # type: ignore
except (ImportError, AttributeError):  # pragma: no cover - optional dependency
    jwt = None  # type: ignore
    RSAAlgorithm = None  # type: ignore

logger = logging.getLogger(__name__)


class SocialVerificationError(Exception):
    def __init__(self, provider: str, message: str):
        super().__init__(message)
        self.provider = provider
        self.message = message


@dataclass
class SocialProfile:
    provider: str
    subject: str
    email: str
    first_name: str | None = None
    last_name: str | None = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'provider': self.provider,
            'subject': self.subject,
            'email': self.email,
            'first_name': self.first_name or '',
            'last_name': self.last_name or '',
        }


GOOGLE_ISSUERS = {'accounts.google.com', 'https://accounts.google.com'}
APPLE_KEYS_URL = 'https://appleid.apple.com/auth/keys'
APPLE_ISSUER = 'https://appleid.apple.com'


def verify_google_token(id_token: str) -> SocialProfile:
    if google_id_token is None or google_requests is None:
        raise SocialVerificationError(
            'google',
            'google-auth library is not installed. Install it with "pip install google-auth".',
        )

    audience = settings.GOOGLE_CLIENT_ID or None

    try:
        request = google_requests.Request()
        payload = google_id_token.verify_oauth2_token(id_token, request, audience=audience)
    except Exception as exc:  # pylint: disable=broad-exception-caught
        logger.exception('Failed to verify Google token: %s', exc)
        raise SocialVerificationError('google', 'Google token validation failed.') from exc

    issuer = payload.get('iss')
    if issuer not in GOOGLE_ISSUERS:
        raise SocialVerificationError('google', 'Unexpected Google token issuer.')

    email = payload.get('email')
    if not email:
        raise SocialVerificationError('google', 'Google token did not include an email address.')

    subject = payload.get('sub')
    if not subject:
        raise SocialVerificationError('google', 'Google token missing subject identifier.')

    return SocialProfile(
        provider='google',
        subject=str(subject),
        email=email,
        first_name=payload.get('given_name'),
        last_name=payload.get('family_name'),
    )


def _fetch_apple_keys() -> Dict[str, Any]:
    if requests is None:
        raise SocialVerificationError(
            'apple',
            'requests library is not installed. Install it with "pip install requests".',
        )

    try:
        response = requests.get(APPLE_KEYS_URL, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as exc:  # pragma: no cover - network issue
        logger.exception('Failed to fetch Apple public keys: %s', exc)
        raise SocialVerificationError('apple', 'Unable to fetch Apple public keys.') from exc


def verify_apple_token(id_token: str) -> SocialProfile:
    if jwt is None or RSAAlgorithm is None:
        raise SocialVerificationError(
            'apple',
            'PyJWT with cryptography support is required. Install it with "pip install pyjwt[crypto]".',
        )

    audience = settings.APPLE_CLIENT_ID or None
    if not audience:
        raise SocialVerificationError('apple', 'Apple client identifier is not configured.')

    try:
        headers = jwt.get_unverified_header(id_token)
    except Exception as exc:  # pylint: disable=broad-exception-caught
        raise SocialVerificationError('apple', 'Invalid Apple identity token header.') from exc

    key_set = _fetch_apple_keys()
    keys = key_set.get('keys', [])
    matching_key = next((key for key in keys if key.get('kid') == headers.get('kid')), None)

    if not matching_key:
        raise SocialVerificationError('apple', 'Unable to match Apple signing key.')

    try:
        public_key = RSAAlgorithm.from_jwk(json.dumps(matching_key))
        payload = jwt.decode(
            id_token,
            public_key,
            algorithms=[headers.get('alg', 'RS256')],
            audience=audience,
            issuer=APPLE_ISSUER,
        )
    except Exception as exc:  # pylint: disable=broad-exception-caught
        logger.exception('Failed to decode Apple identity token: %s', exc)
        raise SocialVerificationError('apple', 'Apple token validation failed.') from exc

    email = payload.get('email')
    if not email:
        raise SocialVerificationError('apple', 'Apple token did not include an email address.')

    subject = payload.get('sub')
    if not subject:
        raise SocialVerificationError('apple', 'Apple token missing subject identifier.')

    return SocialProfile(
        provider='apple',
        subject=str(subject),
        email=email,
        first_name=payload.get('given_name'),
        last_name=payload.get('family_name'),
    )


def verify_social_token(provider: str, id_token: str | None) -> SocialProfile:
    if provider == 'google':
        if not id_token:
            raise SocialVerificationError('google', 'Google ID token was not provided.')
        return verify_google_token(id_token)
    if provider == 'apple':
        if not id_token:
            raise SocialVerificationError('apple', 'Apple identity token was not provided.')
        return verify_apple_token(id_token)
    raise SocialVerificationError(provider, 'Provider is not supported.')
