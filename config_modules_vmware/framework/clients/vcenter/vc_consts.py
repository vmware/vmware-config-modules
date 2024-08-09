# Copyright 2024 Broadcom. All Rights Reserved.
# Vmware REST API related
VC_API_BASE = "https://{}/"

# Vmware REST API session related
VMWARE_API_SESSION_ID = "vmware-api-session-id"
VMWARE_CIS_URL = "https://%s/rest/com/vmware/cis"
SESSION_ID_URL = VMWARE_CIS_URL + "/session"

# CIS task related
CIS_TASKS_URL = "rest/cis/tasks/{}"
CIS_TASK_TERMINAL_STATUS = ("SUCCEEDED", "FAILED")
CIS_TASK_ACTIVE_STATUS = ("PENDING", "RUNNING", "BLOCKED")
CIS_TASK_SUCCEEDED = "SUCCEEDED"
CIS_TASK_FAILED = "FAILED"
CIS_TASK_KEY_VALUE = "value"
CIS_TASK_KEY_STATUS = "status"
CIS_TASK_KEY_RESULT = "result"

# VCSA API appliance related
APPLIANCE_URL_PREFIX = "api/appliance/"
VC_SYSTEM_VERSION_URL = APPLIANCE_URL_PREFIX + "system/version"
NTP_URL = "api/appliance/ntp"
NTP_TEST_URL = "api/appliance/ntp?action=test"
NTP_SERVER_STATUS_REACHABLE = "SERVER_REACHABLE"
NTP_SERVER_STATUS_UNREACHABLE = "SERVER_UNREACHABLE"
TIMESYNC_URL = "api/appliance/timesync"
VC_PROFILE_SETTINGS_URL = "api/appliance/vcenter/settings/v1/config-current?invoker_type=USER"
DESIRED_STATE_SCAN_URL = "api/appliance/vcenter/settings/v1/config?action=scan-desired-state&vmw-task=true"

SYSLOG_URL = "api/appliance/logging/forwarding"
SYSLOG_TEST_URL = "api/appliance/logging/forwarding?action=test"
SYSLOG_SERVER_STATUS_UP = "UP"
SYSLOG_SERVER_STATUS_DOWN = "DOWN"

DNS_URL = "api/appliance/networking/dns/servers"
DNS_TEST_URL = "api/appliance/networking/dns/servers?action=test"
DNS_SERVER_STATUS_GREEN = "green"
DNS_SERVER_STATUS_ORANGE = "orange"
DNS_SERVER_STATUS_RED = "red"

# vSAN MOB related
VSAN_API_VC_SERVICE_ENDPOINT = "/vsanHealth"
VSAN_VMODL_VERSION_3 = "vsan.version.version3"
VSAN_VMODL_URL = "https://{}/sdk/vsanServiceVersions.xml"

# CERT related
CERT_CA_URL = "api/vcenter/certificate-management/vcenter/tls"

# ESXi Host URL
LIST_HOSTS_URL = "api/vcenter/host"

# Backup schedule
BACKUP_SCHEDULE_URL = "api/appliance/recovery/backup/schedules"
BACKUP_SCHEDULE_BY_NAME_URL = "api/appliance/recovery/backup/schedules/{}"
