[![Build Status](https://travis-ci.org/PerimeterX/perimeterx-python-3-wsgi.svg?branch=master)](https://travis-ci.org/PerimeterX/perimeterx-python-3-wsgi)
[![Known Vulnerabilities](https://snyk.io/test/github/PerimeterX/perimeterx-python-3-wsgi/badge.svg)](https://snyk.io/test/github/PerimeterX/perimeterx-python-3-wsgi)

![image](https://storage.googleapis.com/perimeterx-logos/primary_logo_red_cropped.png)

[PerimeterX](http://www.perimeterx.com) Python 3 Middleware
=============================================================
> Latest stable version: [v2.0.0](https://pypi.org/project/perimeterx-python-3-wsgi/)

Table of Contents
-----------------
- [Installation](#installation)
- [Upgrading](#upgrading)
- [Required Configuration](#required_config)
- [Advanced Blocking Response](#advanced_blocking_response)
- [Optional Configuration](#configuration)
    * [Module Enabled](#module_enabled)
    * [Module Mode](#module_mode)
    * [Blocking Score](#blocking_score)
    * [Send Page Activities](#send_page_activities)
    * [Debug Mode](#debug_mode)
    * [Sensitive Routes](#sensitive_routes)
    * [Sensitive Routes Regex](#sensitive_routes_regex)
    * [Whitelist Routes](#whitelist_routes)
    * [Whitelist Routes Regex](#whitelist_routes_regex)
    * [Enforce Specific Routes](#enforce_specific_routes)
    * [Enforce Specific Routes Regex](#enforce_specific_routes_regex)
    * [Monitor Specific Routes](#monitor_specific_routes)
    * [Monitor Specific Routes Regex](#monitor_specific_routes_regex)
    * [Sensitive Headers](#sensitive_headers)
    * [IP Headers](#ip_headers)
    * [First-Party Enabled](#first_party_enabled)
    * [Custom Request Handler](#custom_verification_handler)
    * [Additional Activity Handler](#additional_activity_handler)
    * [Px Disable Request](#px_disable_request)
    * [Test Block Flow on Monitoring Mode](#bypass_monitor_header)
- [Additional Information](#additional_information)

## <a name="installation"></a> Installation

* To install the PerimeterX Python 3 middleware, use PIP as follows:

```python
pip install perimeterx-python-3-wsgi
```

## <a name="upgrading"></a> Upgrading
To upgrade to the latest PerimeterX Enforcer version, run:

`pip install -U perimeterx-python-3-wsgi`

For more information, contact [PerimeterX Support](support@perimeterx.com).

## <a name="required_config"></a> Required Configurations
To use PerimeterX middleware on a specific route follow this example:

```python
from perimeterx.middleware import PerimeterX

px_config = {
    'px_app_id': 'APP_ID',
    'px_cookie_secret': 'COOKIE_SECRET',
    'px_auth_token': 'AUTH_TOKEN',
}
application = get_wsgi_application()
application = PerimeterX(application, px_config)
```
- The PerimeterX **Application ID** / **AppId** and PerimeterX **Token** / **Auth Token** can be found in the Portal, in [Applications](https://console.perimeterx.com/botDefender/admin?page=applicationsmgmt).
- PerimeterX **Risk Cookie** / **Cookie Key** can be found in the portal, in [Policies](https://console.perimeterx.com/botDefender/admin?page=policiesmgmt).
The Policy from where the **Risk Cookie** / **Cookie Key** is taken must correspond with the Application from where the **Application ID** / **AppId** and PerimeterX **Token** / **Auth Token**.
For details on how to create a custom Captcha page, refer to the [documentation](https://docs.perimeterx.com/pxconsole/docs/customize-challenge-page)

## <a name="configuration"></a>Optional Configuration
In addition to the basic installation configuration [above](#required_config), the following configurations options are available:

#### <a name="module_enabled"></a>Module Enabled

A boolean flag to enable/disable the PerimeterX Enforcer.

**Default:** true
```python
config = {
  ...
  px_module_enabled: False
  ...
}
```
#### <a name="module_mode"></a>Module Mode

Sets the working mode of the Enforcer.

Possible values:
* `active_blocking` - Blocking Mode
* `monitor` - Monitoring Mode

**Default:** `monitor` - Monitor Mode

```python
config = {
  ...
  px_module_mode: 'active_blocking'
  ...
}
```
#### <a name="blocking_score"></a>Blocking Score

Sets the minimum blocking score of a request.

Possible values:
* Any integer between 0 and 100.

**Default:** 100
```python
config = {
  ...
  px_blocking_score: 100
  ...
}
```
#### <a name="send_page_activities"></a>Send Page Activities

Enable/disable sending activities and metrics to PerimeterX with each request. <br/>
Enabling this feature allows data to populate the PerimeterX Portal with valuable information, such as the number of requests blocked and additional API usage statistics.

**Default:** true

```python
config = {
  ...
  send_page_activities: True
  ...
}
```

#### <a name="logger_severity"></a>Logger Severity

The severity level at which the logger should output logs
'error' - PerimeterX logger will log errors only on fatal events (e.g., uncaught errors)
'debug' - PerimeterX logger will output detailed logs for debugging purposes

**Default:** 'error'

```python
config = {
  ...
  px_logger_severity: 'debug'
  ...
}
```
#### <a name="sensitive_routes"></a> Sensitive Routes

An array of route prefixes that trigger a server call to PerimeterX servers every time the page is viewed, regardless of viewing history.

**Default:** Empty

```python
config = {
  ...
  px_sensitive_routes: ['/login', '/user/checkout']
  ...
}
```

#### <a name="sensitive_routes_regex"></a> Sensitive Routes Regex

An array of regex patterns that trigger a server call to PerimeterX servers every time the page is viewed, regardless of viewing history.

**Default:** Empty

```python
config = {
  ...
  px_sensitive_routes_regex: [r'^/login$', r'^/user']
  ...
}
```

#### <a name="filtered_routes"></a> Filter By Routes

An array of route prefixes which will bypass enforcement (will never get scored).

**Default:** Empty

```python
config = {
  ...
  px_filter_by_route: ['/about-us', '/careers']
  ...
}
```

#### <a name="whitelist_routes_regex"></a> Whitelist Routes Regex

An array of regex patterns which will bypass enforcement (will never get scored).

**Default:** Empty

```python
config = {
  ...
  whitelist_routes_regex: [r'^/about']
  ...
}
```

#### <a name="enforce_specific_routes"></a> Enforce Specific Routes

An array of route prefixes that are always validated by the PerimeterX Worker (as opposed to whitelisted routes).
When this property is set, any route which is not added - will be whitelisted.

**Default:** Empty

```python
config = {
  ...
  px_enforced_routes: ['/profile']
  ...
};
```

#### <a name="enforce_specific_routes_regex"></a> Enforce Specific Routes Regex

An array of regex patterns that are always validated by the PerimeterX Worker (as opposed to whitelisted routes).
When this property is set, any route which is not added - will be whitelisted.

**Default:** Empty

```python
config = {
  ...
  px_enforced_routes_regex: [r'^/profile$']
  ...
};
```

#### <a name="monitor_specific_routes"></a> Monitor Specific Routes

An array of route prefixes that are always set to be in [monitor mode](#module_mode). This configuration is effective only when the module is enabled and in blocking mode.

**Default:** Empty

```python
config = {
  ...
  px_monitored_routes: ['/profile']
  ...
};
```

#### <a name="monitor_specific_routes_regex"></a> Monitor Specific Routes Regex

An array of regex patterns that are always set to be in [monitor mode](#module_mode). This configuration is effective only when the module is enabled and in blocking mode.

**Default:** Empty

```python
config = {
  ...
  px_monitored_routes_regex: [r'^/profile/me$']
  ...
};
```

#### <a name="sensitive_headers"></a>Sensitive Headers

An array of headers that are not sent to PerimeterX servers on API calls.

**Default:** ['cookie', 'cookies']

```python
config = {
  ...
  px_sensitive_headers: ['cookie', 'cookies', 'x-sensitive-header']
  ...
}
```

#### <a name="ip_headers"></a>IP Headers

An array of trusted headers that specify an IP to be extracted.

**Default:** Empty

```python
config = {
  ...
  px_ip_headers: ['x-user-real-ip']
  ...
}
```

#### <a name="first_party_enabled"></a>First-Party Enabled

Enable/disable First-Party mode.

**Default:** True

```python
config = {
  ...
  px_first_party_enabled: False
  ...
}
```

#### <a name="custom_verification_handler"></a>Custom Verification Handler

A Python function that adds a custom response handler to the request.</br>
You must declare the function before using it in the config.</br>
The Custom Request Handler is triggered after PerimeterX's verification.
The custom function should handle the response (most likely it will create a new response)

**Default:** Empty

```python
config = {
  ...
  px_custom_verification_handler: custom_verification_handler_function,
  ...
}
```
#### <a name="additional_activity_handler"></a>Additional Activity Handler

A Python function that allows interaction with the request data collected by PerimeterX before the data is returned to the PerimeterX servers. Does not alter the response.

**Default:** Empty

```python
config = {
  ...
  px_additional_activity_handler: additional_activity_handler_function,
  ...
}
```

#### <a name="pxde"></a>PerimeterX Data Enrichment

This is a cookie we make available for our costumers, that can provide extra data about the request

```python
context.pxde
context.pxde_verified

```

#### <a name="px_disable_request"></a>Px Disable Request

This is a property that allows the developer to disable the module for a single request. Its value should be True for disabling, and False for enabling

```python
...
environ['px_disable_request'] = False #The request shall be passed to the enforcer.

or

environ['px_disable_request'] = True #The enforcer shall be disabled for that request.

```

#### <a name="bypass_monitor_header"></a> Test Block Flow on Monitoring Mode

Allows you to test an enforcer’s blocking flow while you are still in Monitor Mode.

When the header name is set(eg. `x-px-block`) and the value is set to `1`, when there is a block response (for example from using a User-Agent header with the value of `PhantomJS/1.0`) the Monitor Mode is bypassed and full block mode is applied. If one of the conditions is missing you will stay in Monitor Mode. This is done per request.
To stay in Monitor Mode, set the header value to `0`.

The Header Name is configurable using the `px_bypass_monitor_header` property.

**Default:** Empty

```python
config = {
  ...
  px_bypass_monitor_header: 'x-px-block',
  ...
}
```

## <a name="additional_information"></a> Additional Information
### URI Delimiters
PerimeterX processes URI paths with general- and sub-delimiters according to RFC 3986. General delimiters (e.g., `?`, `#`) are used to separate parts of the URI. Sub-delimiters (e.g., `$`, `&`) are not used to split the URI as they are considered valid characters in the URI path.