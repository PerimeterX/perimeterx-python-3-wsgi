import sys
import time

from werkzeug.wrappers import Request

from perimeterx import px_activities_client
from perimeterx import px_utils
from perimeterx.enums.pass_reason import PassReason
from perimeterx.enums.s2s_error_reason import S2SErrorReason
from perimeterx.px_config import PxConfig
from perimeterx.px_context import PxContext
from perimeterx.px_request_verifier import PxRequestVerifier


class PerimeterX(object):
    def __init__(self, app, config=None):
        self.app = app
        # merging user's defined configurations with the default one
        px_config = PxConfig(config)
        logger = px_config.logger

        if not px_config.app_id:
            logger.error('Unable to initialize module, missing mandatory configuration: app_id')
            raise ValueError('PX App ID is missing')

        if not px_config.auth_token:
            logger.error('Unable to initialize module, missing mandatory configuration: auth_token')
            raise ValueError('PX Auth Token is missing')

        if not px_config.cookie_secret:
            logger.error('Unable to initialize module, missing mandatory configuration: px_cookie')
            raise ValueError('PX Cookie Key is missing')

        self.reverse_proxy_prefix = px_config.app_id[2:].lower()
        self._config = px_config
        self._request_verifier = PxRequestVerifier(px_config)
        px_activities_client.init_activities_configuration(px_config)

    def __call__(self, environ, start_response):
        context = None
        try:
            start = time.time()

            if environ.get('px_disable_request'):
                return self.app(environ, start_response)

            request = Request(environ)
            context, verified_response = self.verify(request)
            pxhd_callback = create_custom_pxhd_callback(context, start_response)
            self._config.logger.debug("PerimeterX Enforcer took: {} ms".format((time.time() - start) * 1000))
            px_activities_client.send_activities_in_thread()
            if verified_response is True:
                return self.app(environ, pxhd_callback)

            return verified_response(environ, pxhd_callback)

        except Exception as err:
            self._config.logger.error(generate_exception())
            self._config.logger.error("Caught exception, passing request. Exception: {}".format(err))
            if context:
                self.report_pass_traffic(context)
            else:
                self.report_pass_traffic(PxContext(Request({}), self._config))
            return self.app(environ, start_response)

    def verify(self, request):
        config = self.config
        logger = config.logger
        logger.debug("Starting request verification {}".format(request.path))
        ctx = None
        try:
            if not config.module_enabled:
                logger.debug('Request will not be verified, module is disabled')
                return ctx, True
            ctx = PxContext(request, config)
            return ctx, self._request_verifier.verify_request(ctx, request)
        except Exception as err:
            logger.error("Caught exception in verify, passing request. Exception: {}".format(err))
            if ctx:
                if ctx.s2s_error_reason == str(S2SErrorReason.NO_ERROR):
                    ctx.pass_reason = str(PassReason.ENFORCER_ERROR)
                    ctx.error_message = generate_exception()

                self.report_pass_traffic(ctx)
            else:
                self.report_pass_traffic(PxContext(Request({}), config))
            return ctx, True

    def report_pass_traffic(self, ctx):
        px_activities_client.send_page_requested_activity(ctx, self.config)

    def report_block_traffic(self, ctx):
        px_activities_client.send_block_activity(ctx, self.config)

    @property
    def config(self):
        return self._config


def create_custom_pxhd_callback(context, start_response):
    def custom_start_response(status, headers, exc_info=None):
        if not context.pxhd or (context.response_pxhd and context.pxhd != context.response_pxhd):
            expiry = px_utils.getExpiryDate()
            headers.append(('Set-Cookie', "_pxhd={}; path=/; expires={}; ".format(context.response_pxhd, expiry)))
        return start_response(status, headers, exc_info)

    return custom_start_response


def generate_exception():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    return 'EXCEPTION IN ({}, LINE {}): {}'.format(filename, lineno, exc_obj)
