import unittest

import mock
from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Request, Response

import perimeterx.px_constants as px_constants
from perimeterx.px_config import PxConfig
from perimeterx.px_context import PxContext
from perimeterx.px_request_verifier import PxRequestVerifier


class TestPxRequestVerifier(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.config = PxConfig({'px_app_id': 'PXfake_app_id',
                               'px_auth_token': '',
                               'px_module_mode': px_constants.MODULE_MODE_BLOCKING
                               })
        cls.headers = {'X-FORWARDED-FOR': '127.0.0.1',
                       'remote-addr': '127.0.0.1',
                       'content_length': '100'}
        cls.request_handler = PxRequestVerifier(cls.config)

    def test_verify_request_fp_client_passed(self):
        builder = EnvironBuilder(headers=self.headers, path='/fake_app_id/init.js')

        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, self.config)
        response = Response("client data")
        with mock.patch('perimeterx.px_proxy.PxProxy.handle_reverse_request', return_value=response):
            response = self.request_handler.verify_request(context, request)
            self.assertEqual(response.data.decode("utf-8"), "client data")

    def test_verify_static_url(self):
        builder = EnvironBuilder(headers=self.headers, path='/fake.css')

        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, self.config)
        response = self.request_handler.verify_request(context, request)
        self.assertEqual(response, True)

    def test_verify_whitelist(self):
        config = PxConfig({'px_app_id': 'PXfake_app_id', 'px_filter_by_route': ['/whitelisted']})
        builder = EnvironBuilder(headers=self.headers, path='/whitelisted')
        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, config)
        response = self.request_handler.verify_request(context, request)
        self.assertEqual(response, True)

    def test_handle_verification_pass(self):
        config = PxConfig({'px_app_id': 'PXfake_app_id', 'px_filter_by_route': ['/whitelisted']})
        builder = EnvironBuilder(headers=self.headers, path='/whitelisted')
        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, config)
        context.score = 50
        response = self.request_handler.verify_request(context, request)
        self.assertEqual(response, True)

    def test_handle_verification_failed(self):
        config = PxConfig({'px_app_id': 'PXfake_app_id', 'px_filter_by_route': ['/whitelisted']})
        builder = EnvironBuilder(headers=self.headers, path='/whitelisted')
        env = builder.get_environ()
        request_handler = PxRequestVerifier(config)
        request = Request(env)
        context = PxContext(request, config)
        context.score = 100
        response = request_handler.verify_request(context, request)
        self.assertEqual(response, True)

    def test_handle_monitor(self):
        config = PxConfig({'px_app_id': 'PXfake_app_id',
                           'px_auth_token': '',
                           'px_module_mode': px_constants.MODULE_MODE_MONITORING
                           })
        request_handler = PxRequestVerifier(config)
        builder = EnvironBuilder(headers=self.headers, path='/')
        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, request_handler.config)
        context.score = 100
        response = request_handler.handle_verification(context, request)
        self.assertEqual(response, True)

    def test_bypass_monitor_header_enabled(self):
        config = PxConfig({'px_app_id': 'PXfake_app_id',
                           'px_auth_token': '',
                           'px_module_mode': px_constants.MODULE_MODE_MONITORING,
                           'px_bypass_monitor_header': 'x-px-block'
                           });
        headers = {'X-FORWARDED-FOR': '127.0.0.1',
                   'remote-addr': '127.0.0.1',
                   'x-px-block': '1',
                   'content_length': '100'}
        request_handler = PxRequestVerifier(config)
        builder = EnvironBuilder(headers=headers, path='/')
        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, request_handler.config)
        context.score = 100
        response = request_handler.handle_verification(context, request)
        self.assertEqual(response.status, '403 Forbidden')

    def test_bypass_monitor_header_disabled(self):
        config = PxConfig({'px_app_id': 'PXfake_app_id',
                           'px_auth_token': '',
                           'px_module_mode': px_constants.MODULE_MODE_MONITORING,
                           'px_bypass_monitor_header': 'x-px-block'
                           });
        headers = {'X-FORWARDED-FOR': '127.0.0.1',
                   'remote-addr': '127.0.0.1',
                   'x-px-block': '0',
                   'content_length': '100'}
        request_handler = PxRequestVerifier(config)
        builder = EnvironBuilder(headers=headers, path='/')
        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, request_handler.config)
        context.score = 100
        response = request_handler.handle_verification(context, request)
        self.assertEqual(response, True)

    def test_bypass_monitor_header_configured_but_missing(self):
        config = PxConfig({'px_app_id': 'PXfake_app_id',
                           'px_auth_token': '',
                           'px_module_mode': px_constants.MODULE_MODE_MONITORING,
                           'px_bypass_monitor_header': 'x-px-block'
                           });
        headers = {'X-FORWARDED-FOR': '127.0.0.1',
                   'remote-addr': '127.0.0.1',
                   'content_length': '100'}
        request_handler = PxRequestVerifier(config)
        builder = EnvironBuilder(headers=headers, path='/')
        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, request_handler.config)
        context.score = 100
        response = request_handler.handle_verification(context, request)
        self.assertEqual(response, True)

    def test_bypass_monitor_header_on_valid_request(self):
        config = PxConfig({'px_app_id': 'PXfake_app_id',
                           'px_auth_token': '',
                           'px_module_mode': px_constants.MODULE_MODE_MONITORING,
                           'px_bypass_monitor_header': 'x-px-block'
                           })
        headers = {'X-FORWARDED-FOR': '127.0.0.1',
                   'remote-addr': '127.0.0.1',
                   'x-px-block': '1',
                   'content_length': '100'}
        request_handler = PxRequestVerifier(config)
        builder = EnvironBuilder(headers=headers, path='/')
        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, request_handler.config)
        context.score = 0
        response = request_handler.handle_verification(context, request)
        self.assertEqual(response, True)

    def test_specific_enforced_routes_with_enforced_route(self):
        config = PxConfig({'px_app_id': 'PXfake_app_id',
                           'px_auth_token': '',
                           'px_module_mode': px_constants.MODULE_MODE_BLOCKING,
                           'px_enforced_routesspecific_routes': ['/profile'],
                           })
        headers = {'X-FORWARDED-FOR': '127.0.0.1',
                   'remote-addr': '127.0.0.1',
                   'content_length': '100'}
        request_handler = PxRequestVerifier(config)
        builder = EnvironBuilder(headers=headers, path='/profile')
        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, request_handler.config)
        context.score = 100
        response = request_handler.handle_verification(context, request)
        self.assertEqual(response.status, '403 Forbidden')

    def test_specific_enforced_routes_with_enforced_route_regex(self):
        config = PxConfig({'px_app_id': 'PXfake_app_id',
                           'px_auth_token': '',
                           'px_module_mode': px_constants.MODULE_MODE_BLOCKING,
                           'px_enforced_routes_regex': [r'^/profile$'],
                           })
        headers = {'X-FORWARDED-FOR': '127.0.0.1',
                   'remote-addr': '127.0.0.1',
                   'content_length': '100'}
        request_handler = PxRequestVerifier(config)
        builder = EnvironBuilder(headers=headers, path='/profile')
        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, request_handler.config)
        context.score = 100
        response = request_handler.handle_verification(context, request)
        self.assertEqual(response.status, '403 Forbidden')

    def test_specific_enforced_routes_with_unenforced_route(self):
        config = PxConfig({'px_app_id': 'PXfake_app_id',
                           'px_auth_token': '',
                           'px_module_mode': px_constants.MODULE_MODE_BLOCKING,
                           'px_enforced_routesspecific_routes': ['/profile'],
                           })
        headers = {'X-FORWARDED-FOR': '127.0.0.1',
                   'remote-addr': '127.0.0.1',
                   'content_length': '100'}
        request_handler = PxRequestVerifier(config)
        builder = EnvironBuilder(headers=headers, path='/')
        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, request_handler.config)
        context.score = 100
        response = request_handler.verify_request(context, request)
        self.assertEqual(response, True)

    def test_specific_enforced_routes_with_unenforced_route_regex(self):
        config = PxConfig({'px_app_id': 'PXfake_app_id',
                           'px_auth_token': '',
                           'px_module_mode': px_constants.MODULE_MODE_BLOCKING,
                           'px_enforced_routes_regex': [r'^/profile$'],
                           })
        headers = {'X-FORWARDED-FOR': '127.0.0.1',
                   'remote-addr': '127.0.0.1',
                   'content_length': '100'}
        request_handler = PxRequestVerifier(config)
        builder = EnvironBuilder(headers=headers, path='/')
        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, request_handler.config)
        context.score = 100
        response = request_handler.verify_request(context, request)
        self.assertEqual(response, True)

    def test_monitor_specific_routes_in_blocking_mode(self):
        config = PxConfig({'px_app_id': 'PXfake_app_id',
                           'px_auth_token': '',
                           'px_module_mode': px_constants.MODULE_MODE_BLOCKING,
                           'px_monitored_routes': ['/profile'],
                           })
        headers = {'X-FORWARDED-FOR': '127.0.0.1',
                   'remote-addr': '127.0.0.1',
                   'content_length': '100'}
        request_handler = PxRequestVerifier(config)
        builder = EnvironBuilder(headers=headers, path='/profile')
        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, request_handler.config)
        response = request_handler.verify_request(context, request)
        self.assertEqual(context.monitored_route, True)
        self.assertEqual(response, True)

    def test_monitor_specific_routes_in_blocking_mode_regex(self):
        config = PxConfig({'px_app_id': 'PXfake_app_id',
                           'px_auth_token': '',
                           'px_module_mode': px_constants.MODULE_MODE_BLOCKING,
                           'px_monitored_routes_regex': [r'^/profile$'],
                           });
        headers = {'X-FORWARDED-FOR': '127.0.0.1',
                   'remote-addr': '127.0.0.1',
                   'content_length': '100'}
        request_handler = PxRequestVerifier(config)
        builder = EnvironBuilder(headers=headers, path='/profile')
        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, request_handler.config)
        response = request_handler.verify_request(context, request)
        self.assertEqual(context.monitored_route, True)

    def test_monitor_specific_routes_in_blocking_mode_should_block_other_routes(self):
        config = PxConfig({'px_app_id': 'PXfake_app_id',
                           'px_auth_token': '',
                           'px_module_mode': px_constants.MODULE_MODE_BLOCKING,
                           'px_monitored_routes': ['/profile'],
                           });
        headers = {'X-FORWARDED-FOR': '127.0.0.1',
                   'remote-addr': '127.0.0.1',
                   'content_length': '100'}
        request_handler = PxRequestVerifier(config)
        builder = EnvironBuilder(headers=headers, path='/')
        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, request_handler.config)
        context.score = 100
        response = request_handler.handle_verification(context, request)
        self.assertEqual(response.status, '403 Forbidden')

    def test_monitor_specific_routes_in_blocking_mode_should_block_other_routes_regex(self):
        config = PxConfig({'px_app_id': 'PXfake_app_id',
                           'px_auth_token': '',
                           'px_module_mode': px_constants.MODULE_MODE_BLOCKING,
                           'px_monitored_routes_regex': [r'^/profile$'],
                           });
        headers = {'X-FORWARDED-FOR': '127.0.0.1',
                   'remote-addr': '127.0.0.1',
                   'content_length': '100'}
        request_handler = PxRequestVerifier(config)
        builder = EnvironBuilder(headers=headers, path='/profile/me')
        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, request_handler.config)
        context.score = 100
        response = request_handler.handle_verification(context, request)
        self.assertEqual(response.status, '403 Forbidden')

    def test_enforced_routes_doesnt_override_monitor_specific_routes(self):
        config = PxConfig({'px_app_id': 'PXfake_app_id',
                           'px_auth_token': '',
                           'px_module_mode': px_constants.MODULE_MODE_BLOCKING,
                           'px_monitored_routes': ['/profile'],
                           'px_enforced_routes': ['/profile', '/login'],
                           })
        headers = {'X-FORWARDED-FOR': '127.0.0.1',
                   'remote-addr': '127.0.0.1',
                   'content_length': '100'}
        request_handler = PxRequestVerifier(config)
        builder = EnvironBuilder(headers=headers, path='/profile')
        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, request_handler.config)
        context.score = 100
        response = request_handler.handle_verification(context, request)
        self.assertEqual(response, True)

    def test_enforced_routes_doesnt_override_monitor_specific_routes(self):
        config = PxConfig({'px_app_id': 'PXfake_app_id',
                           'px_auth_token': '',
                           'px_module_mode': px_constants.MODULE_MODE_BLOCKING,
                           'px_monitored_routes_regex': [r'^/profile$'],
                           'px_enforced_routes_regex': [r'^/profile$', r'^/login$'],
                           })
        headers = {'X-FORWARDED-FOR': '127.0.0.1',
                   'remote-addr': '127.0.0.1',
                   'content_length': '100'}
        request_handler = PxRequestVerifier(config)
        builder = EnvironBuilder(headers=headers, path='/profile')
        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, request_handler.config)
        context.score = 100
        response = request_handler.handle_verification(context, request)
        self.assertEqual(response, True)

    def test_monitor_specific_routes_with_enforced_specific_routes(self):
        config = PxConfig({'px_app_id': 'PXfake_app_id',
                           'px_auth_token': '',
                           'px_module_mode': px_constants.MODULE_MODE_BLOCKING,
                           'px_monitored_routes': ['/profile'],
                           'px_enforced_routes': ['/login'],
                           });
        headers = {'X-FORWARDED-FOR': '127.0.0.1',
                   'remote-addr': '127.0.0.1',
                   'content_length': '100'}
        request_handler = PxRequestVerifier(config)
        builder = EnvironBuilder(headers=headers, path='/profile')
        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, request_handler.config)
        response = request_handler.verify_request(context, request)
        self.assertEqual(context.monitored_route, True)

    def test_monitor_specific_routes_with_enforced_specific_routes_regex(self):
        config = PxConfig({'px_app_id': 'PXfake_app_id',
                           'px_auth_token': '',
                           'px_module_mode': px_constants.MODULE_MODE_BLOCKING,
                           'px_monitored_routes_regex': [r'^/profile$'],
                           'px_enforced_specific_routes_regex': [r'^/login$'],
                           });
        headers = {'X-FORWARDED-FOR': '127.0.0.1',
                   'remote-addr': '127.0.0.1',
                   'content_length': '100'}
        request_handler = PxRequestVerifier(config)
        builder = EnvironBuilder(headers=headers, path='/profile')
        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, request_handler.config)
        response = request_handler.verify_request(context, request)
        self.assertEqual(context.monitored_route, True)
