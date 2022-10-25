# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [2.0.0] - 2022-10-25
### Changed
- Configuration fields' names align with the spec
- Async activities fields align with the spec
- Risk activity fields align with the spec
- Monitored and enforced routes functionality aligned with the spec
- `px_custom_verification_handler` function return `Response` object instead of data, headers and status
- `px_sensitive_routes_regex`, `px_sensitive_routes`, `px_whitelist_routes_regex` and `px_whitelist_routes` configuration fields should contain the exact path
- Changed `debug_mode` configuration field to `px_logger_severity` and change the expected values to `error` and `debug` 

### Fixed
- Remove unnecessary risk api activity fields which might cause a bad request response from the collector

### Added
- Added `request_id` field to the context
- Added implementation for handling s2s_error and enforcer_error.

## [1.2.0] - 2022-04-11
### Added
- New block page implementation
- Configurable max buffer length
- Configurable px_backend_url
- Sending activities at the end of request cycle rather than beginning of the next one

## [1.1.0] - 2020-09-02
### Added
- Support for `monitored_specific_routes`
- Support for Regex patterns in sensitive/whitelist/monitored/enforced routes

## [1.0.1] - 2019-11-10
### Fixed
- Using hashlib pbkdf2 implementation.

## [1.0.0] - 2019-10-29

- Initial release
