from perimeterx.px_config import PxConfig
import unittest
from perimeterx import px_constants
class TestPXConfig(unittest.TestCase):

    def test_constructor(self):
        config_dict = {'px_app_id': 'PXfake_app_id', 'px_logger_severity': 'debug', 'px_module_mode': px_constants.MODULE_MODE_BLOCKING}
        config = PxConfig(config_dict)
        self.assertEqual(config.debug_mode, True)
        self.assertEqual(config.server_host, 'sapi-pxfake_app_id.perimeterx.net')
        self.assertEqual(config.collector_host, 'collector-pxfake_app_id.perimeterx.net')