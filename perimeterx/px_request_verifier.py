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
        if ctx.filtered_route:
            self.logger.debug('The requested uri is whitelisted, passing request')
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

            if config.additional_activity_handler:
                config.additional_activity_handler(ctx, config)
            if ctx.is_monitor_request:
                logger.debug('Monitored request')
                return True
            else:
                data, headers, status = self.px_blocker.handle_blocking(ctx=ctx, config=config)
                response_function = generate_blocking_response(data, headers, status)

        if config.custom_verification_handler:
            logger.debug('custom verification is enabled')
            return config.custom_verification_handler(ctx, self.config, request)

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
