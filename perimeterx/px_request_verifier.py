from werkzeug.wrappers import Response

from perimeterx import px_activities_client
from perimeterx import px_api
from perimeterx import px_blocker
from perimeterx import px_constants
from perimeterx import px_cookie_validator
from perimeterx import px_utils
from perimeterx.px_proxy import PxProxy


class PxRequestVerifier(object):

    def __init__(self, config):
        self.config = config
        self.logger = config.logger
        self._PXBlocker = px_blocker.PXBlocker()

    def verify_request(self, ctx, request):
        uri = ctx.uri
        px_proxy = PxProxy(self.config)
        if px_proxy.should_reverse_request(uri):
            return px_proxy.handle_reverse_request(self.config, ctx, request.get_data())
        if px_utils.is_static_file(ctx):
            self.logger.debug('Filter static file request. uri: {}'.format(uri))
            return True
        if request.environ.get('REQUEST_METHOD') == 'OPTIONS':
            self.logger.debug('The request method was whitelisted, OPTIONS')
            return True
        if ctx.whitelist_route:
            self.logger.debug('The requested uri is whitelisted, passing request')
            return True
        if len(self.config.enforced_specific_routes) > 0 and not ctx.enforced_route:
            self.logger.debug('The request uri {} is not listed in specific routes to enforce, passing request.'.format(uri))
            return True
        # PX Cookie verification
        if not px_cookie_validator.verify(ctx, self.config):
            # Server-to-Server verification fallback
            if not px_api.verify(ctx, self.config):
                self.report_pass_traffic(ctx)
                return True
        return self.handle_verification(ctx, request)

    def handle_verification(self, ctx, request):
        config = self.config
        logger = config.logger
        score = ctx.score
        data = None
        headers = None
        status = None
        pass_request = False
        if score < config.blocking_score:
            logger.debug('Risk score is lower than blocking score')
            self.report_pass_traffic(ctx)
            pass_request = True
        else:
            logger.debug('Risk score is higher or equal than blocking score')
            self.report_block_traffic(ctx)
            should_bypass_monitor = config.bypass_monitor_header and ctx.headers.get(config.bypass_monitor_header) == '1';
            if config.additional_activity_handler:
                config.additional_activity_handler(ctx, config)
            if ctx.monitored_route or (config.module_mode == px_constants.MODULE_MODE_MONITORING and not should_bypass_monitor):
                return True
            else:
                data, headers, status = self.px_blocker.handle_blocking(ctx=ctx, config=config)
                response_function = generate_blocking_response(data, headers, status)

        if config.custom_request_handler:
            data, headers, status = config.custom_request_handler(ctx, self.config, request)
            if data and headers and status:
                return generate_blocking_response(data, headers, status)

        if pass_request:
            return True
        else:
            return response_function

    def report_pass_traffic(self, ctx):
        px_activities_client.send_page_requested_activity(ctx, self.config)

    def report_block_traffic(self, ctx):
        px_activities_client.send_block_activity(ctx, self.config)

    @property
    def px_blocker(self):
        return self._PXBlocker


def generate_blocking_response(data, headers, status):
    result = Response(data)
    if headers is not None:
        result.headers = headers
    if status is not None:
        result.status = status
    return result
