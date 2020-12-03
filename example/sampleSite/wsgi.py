"""
WSGI config for sampleSite project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os
import json
from django.core.wsgi import get_wsgi_application

from perimeterx.middleware import PerimeterX
from perimeterx import px_constants

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sampleSite.settings")


def custom_request_handler(ctx, config, environ):
    headers = ctx.headers
    if headers.get('x-px-auto-tests') and headers.get('x-px-auto-tests') == 'bigbotsdontcry':
        result = {
            'px_cookies': ctx.px_cookies,
            'vid': ctx.vid,
            'ip': ctx.ip,
            'full_url': ctx.full_url,
            'score': ctx.score,
            'px_cookie_hmac': ctx.cookie_hmac,
            'block_action': ctx.block_action,
            'http_method': ctx.http_method,
            'hostname': ctx.hostname,
            'headers': ctx.headers._store,
            'user_agent': ctx.user_agent,
            'uri': ctx.uri,
            'is_made_s2s_api_call': True if ctx.s2s_call_reason != 'none' else False,
            'sensitive_route': ctx.sensitive_route,
            'decoded_px_cookie': ctx.decoded_cookie,
            'cookie_origin': ctx.cookie_origin,
            'http_version': ctx.http_version,
            's2s_call_reason': ctx.s2s_call_reason,
            'block_reason': ctx.block_reason,
            'module_mode': 1 if config.module_mode is px_constants.MODULE_MODE_BLOCKING else 0,
            'pxde': ctx.pxde,
            'risk_rtt': ctx.risk_rtt,
            'uuid': ctx.uuid,
            'pxde_verified': ctx.pxde_verified,
        }
        if ctx.original_uuid:
            result['original_uuid'] = ctx.original_uuid
        if ctx.original_token_error:
            result['original_token_error'] = ctx.original_token_error

        response_headers = [('Content-Type', 'application/json')]
        return json.dumps(result), response_headers, '200 OK'
    return None, None, None


px_config = {
    'app_id': 'REPLACE',
    'cookie_key': 'REPLACE',
    'auth_token': 'REPLACE',
    'blocking_score': 60,
    'debug_mode': True,
    'module_mode': px_constants.MODULE_MODE_BLOCKING,
    'custom_logo': 'https://camo.githubusercontent.com/5a6225194534d62175a3682df3565eb5494b2c1f/687474703a2f2f6d656469612e6d61726b6574776972652e636f6d2f6174746163686d656e74732f3230313630342f33343231355f506572696d65746572585f6c6f676f2e6a7067',
    'css_ref': 'https://bootswatch.com/cyborg/bootstrap.min.css',
    'js_ref': 'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js',
    'custom_request_handler': custom_request_handler,
    'first_party': True,
    'ip_headers': ['x-forwarded-for'],
    'sensitive_routes': ['/profile', '/testjs']
}

application = get_wsgi_application()
application = PerimeterX(application, px_config)
