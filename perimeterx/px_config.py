from perimeterx import px_constants
from perimeterx.px_testing_mode_handler import testing_mode_handling
from perimeterx.px_logger import Logger
import os

class PxConfig(object):
    def __init__(self, config_dict):
        app_id = config_dict.get('px_app_id')
        self._px_app_id = app_id
        logger_severity = config_dict.get('px_logger_severity', 'error')
        module_mode = config_dict.get('px_module_mode', px_constants.MODULE_MODE_MONITORING)
        self._custom_logo = config_dict.get('px_custom_logo', None)
        testing_mode = config_dict.get('testing_mode', False)
        px_backend_host = config_dict.get('px_backend_url', None)
        max_buffer_len = config_dict.get('px_max_activity_batch_size', 20)
        self._blocking_score = config_dict.get('px_blocking_score', 100)
        self._logger_severity = logger_severity
        self._module_version = config_dict.get('module_version', px_constants.MODULE_VERSION)
        self._module_version = px_constants.MODULE_VERSION.format(' GAE') if os.environ.get('SERVER_SOFTWARE','').startswith('Google') else px_constants.MODULE_VERSION.format('')
        self._module_mode = module_mode
        self._server_host = px_backend_host if px_backend_host else 'sapi.perimeterx.net' if app_id is None else px_constants.SERVER_URL.format(app_id.lower())
        self._collector_host = px_backend_host if px_backend_host else 'collector.perimeterx.net' if app_id is None else px_constants.COLLECTOR_URL.format(app_id.lower())
        self._encryption_enabled = config_dict.get('px_encryption_enabled', True)
        self._sensitive_headers = [*map(lambda header: header.lower(),
                                      config_dict.get('px_sensitive_headers', ['cookie', 'cookies']))]
        self._send_page_activities = config_dict.get('px_send_page_activities', True)
        self._api_timeout_ms = config_dict.get('api_timeout', 1000)
        self._css_ref = config_dict.get('px_css_ref', '')
        self._js_ref = config_dict.get('px_js_ref', '')
        self._module_enabled = config_dict.get('px_module_enabled', True)
        self._auth_token = config_dict.get('px_auth_token', None)
        self._first_party_enabled = config_dict.get('px_first_party_enabled', True)
        self._first_party_xhr_enabled = config_dict.get('px_first_party_xhr_enabled', True)
        self._ip_headers = config_dict.get('px_ip_headers', [])
        self._proxy_url = config_dict.get('px_proxy_url', None)
        self._bypass_monitor_header = config_dict.get('px_bypass_monitor_header','')
        self._max_buffer_len = max_buffer_len if max_buffer_len > 0 else 1

        sensitive_routes = config_dict.get('px_sensitive_routes', [])
        if not isinstance(sensitive_routes, list):
            raise TypeError('sensitive_routes must be a list')
        self._sensitive_routes = sensitive_routes

        filter_by_route = config_dict.get('px_filter_by_route', [])
        if not isinstance(filter_by_route, list):
            raise TypeError('px_filter_by_route must be a list')
        self._filter_by_route = filter_by_route

        enforced_routes = config_dict.get('px_enforced_routes', [])
        if not isinstance(enforced_routes, list):
            raise TypeError('enforced_routes must be a list')
        self._enforced_specific_routes = enforced_routes

        monitored_routes = config_dict.get('px_monitored_routes', [])
        if not isinstance(monitored_routes, list):
            raise TypeError('monitored_routes must be a list')
        self._monitored_specific_routes = monitored_routes

        sensitive_routes_regex = config_dict.get('px_sensitive_routes_regex', [])
        if not isinstance(sensitive_routes_regex, list):
            raise TypeError('sensitive_routes_regex must be a list')
        self._sensitive_routes_regex = sensitive_routes_regex

        whitelist_routes_regex = config_dict.get('px_filter_by_route_regex', [])
        if not isinstance(whitelist_routes_regex, list):
            raise TypeError('whitelist_routes_regex must be a list')
        self._whitelist_routes_regex = whitelist_routes_regex

        enforced_routes_regex = config_dict.get('px_enforced_routes_regex', [])
        if not isinstance(enforced_routes_regex, list):
            raise TypeError('enforced_specific_routes must be a list')
        self._enforced_specific_routes_regex = enforced_routes_regex

        monitored_routes_regex = config_dict.get('px_monitored_routes_regex', [])
        if not isinstance(monitored_routes_regex, list):
            raise TypeError('monitored_specific_routes_regex must be a list')
        self._monitored_specific_routes_regex = monitored_routes_regex
        self._telemetry_config = self.__create_telemetry_config()
        self._testing_mode = testing_mode
        self._auth_token = config_dict.get('px_auth_token', None)
        self._cookie_secret = config_dict.get('px_cookie_secret', None)
        self.__instantiate_user_defined_handlers(config_dict)
        self._logger = Logger(logger_severity, app_id)
        if testing_mode:
            self._custom_verification_handler = testing_mode_handling

    @property
    def module_mode(self):
        return self._module_mode

    @property
    def app_id(self):
        return self._px_app_id

    @property
    def logger(self):
        return self._logger

    @property
    def auth_token(self):
        return self._auth_token

    @property
    def cookie_secret(self):
        return self._cookie_secret

    @property
    def server_host(self):
        return self._server_host

    @property
    def api_timeout(self):
        return self._api_timeout_ms / 1000.000

    @property
    def module_enabled(self):
        return self._module_enabled

    @property
    def ip_headers(self):
        return self._ip_headers

    @property
    def sensitive_headers(self):
        return self._sensitive_headers

    @property
    def proxy_url(self):
        return self._proxy_url

    @property
    def custom_verification_handler(self):
        return self._custom_verification_handler

    @property
    def blocking_score(self):
        return self._blocking_score

    @property
    def encryption_enabled(self):
        return self._encryption_enabled

    @property
    def module_version(self):
        return self._module_version

    @property
    def send_page_activities(self):
        return self._send_page_activities

    @property
    def custom_logo(self):
        return self._custom_logo

    @property
    def css_ref(self):
        return self._css_ref

    @property
    def js_ref(self):
        return self._js_ref

    @property
    def first_party_enabled(self):
        return self._first_party_enabled

    @property
    def first_party_xhr_enabled(self):
        return self._first_party_xhr_enabled

    @property
    def collector_host(self):
        return self._collector_host

    @property
    def get_user_ip(self):
        return self._get_user_ip

    @property
    def sensitive_routes(self):
        return self._sensitive_routes

    @property
    def filter_by_route(self):
        return self._filter_by_route

    @property
    def sensitive_routes_regex(self):
        return self._sensitive_routes_regex

    @property
    def whitelist_routes_regex(self):
        return self._whitelist_routes_regex

    @property
    def additional_activity_handler(self):
        return self._additional_activity_handler

    @property
    def debug_mode(self):
        return self._logger_severity == 'debug'

    @property
    def max_buffer_len(self):
        return self._max_buffer_len

    @property
    def telemetry_config(self):
        return self._telemetry_config

    @property
    def enrich_custom_parameters(self):
        return self._enrich_custom_parameters

    @property
    def testing_mode(self):
        return self._testing_mode

    @property
    def bypass_monitor_header(self):
        return self._bypass_monitor_header

    @property
    def enforced_specific_routes(self):
        return self._enforced_specific_routes

    @property
    def monitored_specific_routes(self):
        return self._monitored_specific_routes

    @property
    def enforced_specific_routes_regex(self):
        return self._enforced_specific_routes_regex

    @property
    def monitored_specific_routes_regex(self):
        return self._monitored_specific_routes_regex

    def __instantiate_user_defined_handlers(self, config_dict):
        self._custom_verification_handler = self.__set_handler('px_custom_verification_handler', config_dict)
        self._get_user_ip = self.__set_handler('get_user_ip', config_dict)
        self._additional_activity_handler = self.__set_handler('px_additional_activity_handler', config_dict)
        self._enrich_custom_parameters = self.__set_handler('px_enrich_custom_parameters', config_dict)

    def __set_handler(self, function_name, config_dict):
        return config_dict.get(function_name) if config_dict.get(function_name) and callable(
            config_dict.get(function_name)) else None

    def __create_telemetry_config(self):
        config = self.__dict__
        mutated_config = {}
        for key, value in config.items():
            mutated_config[key[1:].upper()] = value
        return mutated_config