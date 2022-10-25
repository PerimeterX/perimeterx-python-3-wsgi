import json
import time
import os
import requests

# pylint: disable=import-error
from perimeterx.enums.pass_reason import PassReason
from perimeterx.enums.s2s_error_reason import S2SErrorReason
from perimeterx.px_constants import MODULE_MODE_BLOCKING

if os.environ.get('SERVER_SOFTWARE', '').startswith('Google'):
    import requests_toolbelt.adapters.appengine

    requests_toolbelt.adapters.appengine.monkeypatch()
# pylint: enable=import-error

from perimeterx import px_constants
from perimeterx import px_httpc
from perimeterx import px_utils

custom_params = {
    'custom_param1': '',
    'custom_param2': '',
    'custom_param3': '',
    'custom_param4': '',
    'custom_param5': '',
    'custom_param6': '',
    'custom_param7': '',
    'custom_param8': '',
    'custom_param9': '',
    'custom_param10': ''
}


def send_risk_request(ctx, config):
    """
    :param PxContext ctx:
    :param PxConfig config:
    :return dict:
    """
    start = time.time()
    body = prepare_risk_body(ctx, config)
    default_headers = {
        'Authorization': 'Bearer ' + config.auth_token,
        'Content-Type': 'application/json'
    }
    try:
        response = px_httpc.send(full_url=config.server_host + px_constants.API_RISK, body=json.dumps(body),
                                 config=config, headers=default_headers, method='POST', raise_error=True)

        if response is None:
            ctx.pass_reason = str(PassReason.S2S_ERROR)
            handle_s2s_error(ctx, response, str(S2SErrorReason.INVALID_RESPONSE), None)
            return False

        if response.status_code != 200:
            handle_unexpected_http_status_error(ctx, response, config)
            return False

        config.logger.debug('Risk response: {}'.format(response.content))
        json_response = json.loads(response.content)

        if not json_response or type(json_response) is not dict:
            handle_s2s_error(ctx, response, str(S2SErrorReason.INVALID_RESPONSE), None)
            return False

        ctx.uuid = json_response.get('uuid')

        if not is_valid_response(json_response):
            handle_s2s_error(ctx, response, str(S2SErrorReason.REQUEST_FAILED_ON_SERVER), None)
            return False

        return json_response

    except requests.exceptions.Timeout:
        ctx.pass_reason = str(PassReason.S2S_TIMEOUT)
        risk_rtt = time.time() - start
        config.logger.debug('Risk API timed out, round_trip_time: {}'.format(risk_rtt))
        return False
    except ValueError as e:
        handle_s2s_error(ctx, response, str(S2SErrorReason.INVALID_RESPONSE), e)
        config.logger.debug('Unexpected exception in Risk API call, the response is invalid: {}'.format(e))
        return False
    except requests.exceptions.RequestException as e:
        handle_s2s_error(ctx, response, str(S2SErrorReason.INVALID_RESPONSE), e)
        config.logger.debug('Unexpected exception in Risk API call: {}'.format(e))
        return False
    except Exception as e:
        handle_s2s_error(ctx, response, str(S2SErrorReason.UNKNOWN_ERROR), e)
        config.logger.debug('Unexpected exception in Risk API call: {}'.format(e))
        return False


def is_valid_response(response):
    return response.get('status') == 0


def handle_unexpected_http_status_error(ctx, response, config):
    logger = config.logger
    ctx.pass_reason = str(PassReason.S2S_ERROR)
    error_reason = str(S2SErrorReason.UNKNOWN_ERROR)
    response_status = response.status_code

    if 500 <= response_status < 600:
        error_reason = str(S2SErrorReason.SERVER_ERROR)
    elif 400 <= response_status < 500:
        error_reason = str(S2SErrorReason.BAD_REQUEST)

    logger.debug('Risk API returned status {}, {}'.format(response_status, error_reason))
    ctx.s2s_error_reason = error_reason
    ctx.error_message = str(response.content)
    ctx.s2s_error_http_status = response_status
    ctx.s2s_error_http_message = response.reason


def handle_s2s_error(ctx, response, s2s_error_reason, exception):
    """
       :param s2s_error_reason:
       :param response: Response
       :param exception: Exception
       :param PxContext ctx: PxContext
       :return bool: is request verified
       """

    ctx.s2s_error_reason = s2s_error_reason
    ctx.pass_reason = str(PassReason.S2S_ERROR)

    if response is not None and response.status_code:
        ctx.s2s_error_http_status = response.status_code

    ctx.error_message = str(exception) if exception else 'error'


def verify(ctx, config):
    """
    :param PxContext ctx:
    :param pxConfig config:
    :return bool: is request verified
    """

    logger = config.logger
    logger.debug('Evaluating Risk API request, call reason: {}'.format(ctx.s2s_call_reason))
    try:
        start = time.time()
        response = send_risk_request(ctx, config)
        risk_rtt = time.time() - start
        logger.debug('Risk call took {} ms'.format(risk_rtt))

        if response:
            ctx.score = response.get('score')
            ctx.block_action = response.get('action')
            ctx.risk_rtt = risk_rtt
            ctx.pxde = response.get('data_enrichment', {})
            ctx.pxde_verified = True
            response_pxhd = response.get('pxhd', '')
            # Do not set cookie if there's already a valid pxhd
            ctx.response_pxhd = response_pxhd
            if ctx.score >= config.blocking_score:
                if response.get('action') == px_constants.ACTION_CHALLENGE and \
                        response.get('action_data') is not None and \
                        response.get('action_data').get('body') is not None:

                    logger.debug("received javascript challenge action")
                    ctx.block_action_data = response.get('action_data').get('body')
                    ctx.block_reason = 'challenge'

                elif response.get('action') is px_constants.ACTION_RATELIMIT:
                    logger.debug("received javascript ratelimit action")
                    ctx.block_reason = 'exceeded_rate_limit'

                else:
                    logger.debug("block score threshold reached, will initiate blocking")
                    ctx.block_reason = 's2s_high_score'
            else:
                ctx.pass_reason = str(PassReason.S2S)

            msg = 'Risk API response returned successfully, risk score: {}, round_trip_time: {} ms'
            logger.debug(msg.format(ctx.score, risk_rtt))
            return True
        else:
            return False
    except Exception as err:
        logger.error('Risk API request failed. Error: {}'.format(err))
        handle_s2s_error(ctx, response, str(S2SErrorReason.UNKNOWN_ERROR), err)
        return False


def prepare_risk_body(ctx, config):
    logger = config.logger
    risk_mode = 'monitor' if config.module_mode == px_constants.MODULE_MODE_MONITORING or ctx.monitored_route else MODULE_MODE_BLOCKING

    body = {
        'request': {
            'ip': ctx.ip,
            'headers': format_headers(ctx.headers),
            'url': ctx.full_url
        },
        'additional': {
            's2s_call_reason': ctx.s2s_call_reason,
            'http_method': ctx.http_method,
            'http_version': ctx.http_version,
            'module_version': config.module_version,
            'risk_mode': risk_mode,
            'cookie_origin': ctx.cookie_origin,
            'request_id': ctx.request_id
        }
    }
    if ctx.vid:
        body['vid'] = ctx.vid
        body['additional']['enforcer_vid_source'] = ctx.enforcer_vid_source
    if ctx.uuid:
        body['uuid'] = ctx.uuid
    if ctx.cookie_hmac:
        body['additional']['px_cookie_hmac'] = ctx.cookie_hmac
    if ctx.cookie_names:
        body['additional']['request_cookie_names'] = ctx.cookie_names
    if ctx.pxhd:
        body['pxhd'] = ctx.pxhd

    body = add_original_token_data(ctx, body)

    px_utils.prepare_custom_params(config, body['additional'])

    if ctx.s2s_call_reason == 'cookie_decryption_failed':
        logger.debug('attaching orig_cookie to request')
        body['additional']['px_cookie_raw'] = ctx.px_cookie_raw

    if ctx.s2s_call_reason in ['cookie_expired', 'cookie_validation_failed']:
        logger.debug('attaching px_cookie to request')
        body['additional']['px_cookie'] = ctx.decoded_cookie

    return body


def add_original_token_data(ctx, body):
    if ctx.original_uuid:
        body['additional']['original_uuid'] = ctx.original_uuid
    if ctx.original_token_error:
        body['additional']['original_token_error'] = ctx.original_token_error
    if ctx.original_token:
        body['additional']['original_token'] = ctx.original_token
    if ctx.decoded_original_token:
        body['additional']['decoded_original_token'] = ctx.decoded_original_token
    return body


def format_headers(headers):
    ret_val = []
    for key in headers.keys():
        ret_val.append({'name': key, 'value': headers[key]})
    return ret_val
