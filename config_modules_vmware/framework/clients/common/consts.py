# Copyright 2024 Broadcom. All Rights Reserved.
import ssl

# Rest client related
HTTPS_URL = "https://"
SSL_VERIFY_CA_PATH = "/etc/ssl/certs/vmware"
TLS_VERSION = ssl.PROTOCOL_TLSv1_2
CERT_REQUIRED = "CERT_REQUIRED"
CERT_NONE = "CERT_NONE"
JSON_REQUEST_HEADERS = {"Content-Type": "application/json"}

# VC SSO client related
STS_PATH = "https://{}/sts/STSService/{}"
SSO_PATH = "/sso-adminserver/sdk/{}"
SSO_SERVICE_INSTANCE = "SsoAdminServiceInstance"
SSO_TLS_VERSION = ssl.PROTOCOL_TLS

# Constants regarding time
SECS_5 = 5
SECS_10 = 10
SECS_15 = 15
SECS_30 = 30
SECS_60 = 60
SECS_75 = 75
SECS_IN_2_MINS = 2 * 60  # Number of seconds in 2 minutes
SECS_IN_3_MINS = 3 * 60  # Number of seconds in 3 minutes
SECS_IN_5_MINS = 5 * 60  # Number of seconds in 5 minutes
SECS_IN_10_MINS = 10 * 60  # Number of seconds in 10 minutes
SECS_IN_15_MINS = 15 * 60  # Number of seconds in 15 minutes
SECS_IN_30_MINS = 30 * 60  # Number of seconds in 30 minutes
SECS_IN_60_MINS = 60 * 60  # Number of seconds in 60 minutes

# check compliance, precheck, remediate response related
STATUS = "status"
RESULT = "result"
SUMMARY = "summary"
VALUE = "value"
KEY = "key"
CHANGES = "changes"
HOST_CHANGES = "host_changes"
HOST_RESULTS = "host_results"
NAME = "name"
MESSAGE = "message"
OLD = "old"
NEW = "new"
CURRENT = "current"
DESIRED = "desired"
ERRORS = "errors"
GLOBAL = "global"
SKIPPED = "SKIPPED"
COMPLIANCE_CONFIG = "compliance_config"
METADATA = "metadata"
UNSUPPORTED_VERSION_MESSAGE_FORMAT = "Version [{}] is not supported for product [{}]"
# Timestamp format
DEFAULT_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"

# Message consts for skipped workflows
REMEDIATION_SKIPPED_MESSAGE = "Remediation is not implemented as this control requires manual intervention"
CONTROL_ALREADY_COMPLIANT = "Control already compliant"
CONTROL_NOT_APPLICABLE = "Control is not applicable on this product version"
CONTROL_NOT_AUTOMATED = "Control is not automated for this product version"
