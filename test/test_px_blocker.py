import os
import unittest
import json

from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Request
from perimeterx import px_constants
from perimeterx.px_blocker import PXBlocker
from perimeterx.px_config import PxConfig
from perimeterx.px_context import PxContext
from perimeterx.px_request_verifier import PxRequestVerifier
from werkzeug.wrappers import Response


def custom_verification_handler(ctx, config, request):
    result = {
        'score': ctx.score
    }

    data = json.dumps(result)
    response = Response(data)
    response.headers = {'testing': 'testing'}
    response.status = '303 OK'

    return response


class Test_PXBlocker(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.config = PxConfig({'px_app_id': 'PXfake_app_id'})
        cls.headers = {'X-FORWARDED-FOR': '127.0.0.1',
                       'remote-addr': '127.0.0.1',
                       'content-length': '100'}
        cls.request_handler = PxRequestVerifier(cls.config)

    def test_is_json_response(self):
        px_blocker = PXBlocker()
        builder = EnvironBuilder(headers=self.headers, path='/fake_app_id/init.js')

        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, self.config)
        self.assertFalse(px_blocker.is_json_response(context))
        context.headers['Accept'] = 'application/json'
        self.assertTrue(px_blocker.is_json_response(context))

    def test_handle_blocking(self):
        px_blocker = PXBlocker()
        vid = 'bf619be8-94be-458a-b6b1-ee81f154c282'
        px_uuid = '8712cef7-bcfa-4bb6-ae99-868025e1908a'

        builder = EnvironBuilder(headers=self.headers, path='/fake_app_id/init.js')

        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, self.config)
        context.vid = vid
        context.uuid = px_uuid
        px_config = PxConfig({'px_app_id': 'PXfake_app_id'})
        message, _, _ = px_blocker.handle_blocking(context, px_config)
        working_dir = os.path.dirname(os.path.realpath(__file__))
        with open(working_dir + '/px_blocking_messages/blocking.txt', 'r') as myfile:
            blocking_message = myfile.read()

        self.assertEqual(message, blocking_message)

    def test_handle_ratelimit(self):
        px_blocker = PXBlocker()
        vid = 'bf619be8-94be-458a-b6b1-ee81f154c282'
        px_uuid = '8712cef7-bcfa-4bb6-ae99-868025e1908a'
        config = PxConfig({'px_app_id': 'PXfake_app_id'})
        builder = EnvironBuilder(headers=self.headers, path='/fake_app_id/init.js')

        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, self.config)
        context.vid = vid
        context.uuid = px_uuid
        context.block_action = 'r'
        message, _, _ = px_blocker.handle_blocking(context, config)
        blocking_message = None
        working_dir = os.path.dirname(os.path.realpath(__file__))
        with open(working_dir + '/px_blocking_messages/ratelimit.txt', 'r') as myfile:
            blocking_message = myfile.read()
        self.assertEqual(message, blocking_message)

    def test_handle_challenge(self):
        px_blocker = PXBlocker()
        vid = 'bf619be8-94be-458a-b6b1-ee81f154c282'
        px_uuid = '8712cef7-bcfa-4bb6-ae99-868025e1908a'
        builder = EnvironBuilder(headers=self.headers, path='/fake_app_id/init.js')

        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, self.config)
        context.vid = vid
        context.uuid = px_uuid
        context.block_action = 'j'
        context.block_action_data = 'Bla'

        message, _, _ = px_blocker.handle_blocking(context, self.config)
        blocking_message = 'Bla'
        self.assertEqual(message, blocking_message)

    def test_prepare_properties(self):
        px_blocker = PXBlocker()
        vid = 'bf619be8-94be-458a-b6b1-ee81f154c282'
        px_uuid = '8712cef7-bcfa-4bb6-ae99-868025e1908a'
        builder = EnvironBuilder(headers=self.headers, path='/fake_app_id/init.js')

        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, self.config)
        context.vid = vid
        context.uuid = px_uuid
        message = px_blocker.prepare_properties(context, self.config)
        expected_message = {'blockScript': '/fake_app_id/captcha/captcha.js?a=&u=8712cef7-bcfa-4bb6-ae99-868025e1908a&v=bf619be8-94be-458a-b6b1-ee81f154c282&m=0',
                            'vid': 'bf619be8-94be-458a-b6b1-ee81f154c282',
                            'jsRef': '',
                            'hostUrl': '/fake_app_id/xhr',
                            'customLogo': '',
                            'appId': 'PXfake_app_id',
                            'uuid': '8712cef7-bcfa-4bb6-ae99-868025e1908a',
                            'jsClientSrc': '/fake_app_id/init.js',
                            'firstPartyEnabled': 'true',
                            'cssRef': '',
                            'altBlockScript': '//captcha.px-cloud.net/PXfake_app_id/captcha.js?a=&u=8712cef7-bcfa-4bb6-ae99-868025e1908a&v=bf619be8-94be-458a-b6b1-ee81f154c282&m=0'}
        self.assertDictEqual(message, expected_message)
        expected_message['blockScript'] = '/fake_app/captcha/captcha.js?a=&u=8712cef7-bcfa-4bb6-ae99-868025e1908a&v=bf619be8-94be-458a-b6b1-ee81f154c282&m=0'
        self.assertNotEqual(message, expected_message)

    def test_custom_verification_handler(self):
        config = PxConfig({'px_app_id': 'app_id',
                           'px_module_mode': px_constants.MODULE_MODE_BLOCKING,
                           'px_custom_verification_handler': custom_verification_handler})
        builder = EnvironBuilder(headers=self.headers, path='/')
        request_handler = PxRequestVerifier(config)
        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, config)
        context.score = 100
        response = request_handler.handle_verification(context, request)
        self.assertNotEqual(response.status_code, 403)
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers['testing'], 'testing')

    def test_monitored_routes_monitor_request_that_should_be_blocked(self):
        config = PxConfig({'px_app_id': 'app_id',
                           'px_module_mode': px_constants.MODULE_MODE_BLOCKING,
                           'px_monitored_routes': ['/profile']})
        builder = EnvironBuilder(headers=self.headers, path='/profile')
        request_handler = PxRequestVerifier(config)
        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, config)
        context.score = 100
        response = request_handler.handle_verification(context, request)
        self.assertTrue(response)

    def test_monitored_routes_block_request_that_shouldnt_be_monitored(self):
        config = PxConfig({'px_app_id': 'app_id',
                           'px_module_mode': px_constants.MODULE_MODE_BLOCKING,
                           'px_monitored_routes': ['/profile']})
        builder = EnvironBuilder(headers=self.headers, path='/pro')
        request_handler = PxRequestVerifier(config)
        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, config)
        context.score = 100
        response = request_handler.handle_verification(context, request)
        self.assertEqual(response.status_code, 403)

    def test_monitored_routes_regex_monitor_request_that_should_be_monitored(self):
        config = PxConfig({'px_app_id': 'app_id',
                           'px_module_mode': px_constants.MODULE_MODE_BLOCKING,
                           'px_monitored_routes_regex': ['/profile.*']})
        builder = EnvironBuilder(headers=self.headers, path='/profile/test')
        request_handler = PxRequestVerifier(config)
        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, config)
        context.score = 100
        response = request_handler.handle_verification(context, request)
        self.assertTrue(response)

    def test_enforced_routes_block_request_in_monitor_mode(self):
        config = PxConfig({'px_app_id': 'app_id',
                           'px_module_mode': px_constants.MODULE_MODE_MONITORING,
                           'px_enforced_routes': ['/profile']})
        builder = EnvironBuilder(headers=self.headers, path='/profile')
        request_handler = PxRequestVerifier(config)
        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, config)
        context.score = 100
        response = request_handler.handle_verification(context, request)
        self.assertEqual(response.status_code, 403)

    def test_enforced_routes_regex_block_request_in_monitor_mode(self):
        config = PxConfig({'px_app_id': 'app_id',
                           'px_module_mode': px_constants.MODULE_MODE_MONITORING,
                           'px_enforced_routes_regex': ['/profile.*']})
        builder = EnvironBuilder(headers=self.headers, path='/profile')
        request_handler = PxRequestVerifier(config)
        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, config)
        context.score = 100
        response = request_handler.handle_verification(context, request)
        self.assertEqual(response.status_code, 403)

    def test_bypass_monitor_header_block_request_in_monitor_mode(self):
        config = PxConfig({'px_app_id': 'app_id',
                           'px_module_mode': px_constants.MODULE_MODE_MONITORING,
                           'px_bypass_monitor_header': 'bypass-header'})
        self.headers.update({'bypass-header': px_constants.BYPASS_MONITOR_HEADER})
        builder = EnvironBuilder(headers=self.headers, path='/profile')
        request_handler = PxRequestVerifier(config)
        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, config)
        context.score = 100
        response = request_handler.handle_verification(context, request)
        self.assertEqual(response.status_code, 403)

    def test_filter_by_route(self):
        config = PxConfig({'px_app_id': 'app_id',
                           'px_module_mode': px_constants.MODULE_MODE_BLOCKING,
                           'px_filter_by_route': ['/profile']})
        self.headers.update({'bypass-header': px_constants.BYPASS_MONITOR_HEADER})
        builder = EnvironBuilder(headers=self.headers, path='/profile')
        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, config)
        context.score = 100
        response = self.request_handler.verify_request(context, request)
        self.assertTrue(response)

    def test_filter_by_route_regex(self):
        config = PxConfig({'px_app_id': 'app_id',
                           'px_module_mode': px_constants.MODULE_MODE_BLOCKING,
                           'px_filter_by_route_regex': ['/profile.*']})
        self.headers.update({'bypass-header': px_constants.BYPASS_MONITOR_HEADER})
        builder = EnvironBuilder(headers=self.headers, path='/profile/test')
        env = builder.get_environ()
        request = Request(env)
        context = PxContext(request, config)
        context.score = 100
        response = self.request_handler.verify_request(context, request)
        self.assertTrue(response)



