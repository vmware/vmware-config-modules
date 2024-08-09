# Copyright 2024 Broadcom. All Rights Reserved.
# SDDC Manager REST APIs
SDDC_MANAGER_API_BASE = "https://{}/"
SDDC_MANAGER_TOKEN_URL = SDDC_MANAGER_API_BASE + "v1/tokens/"
SDDC_MANAGER_ACCESS_TOKEN = "accessToken"  # nosec

# Vmware REST API session related
NTP_URL = "v1/system/ntp-configuration"
DNS_URL = "v1/system/dns-configuration"
BACKUP_URL = "v1/system/backup-configuration"
FIPS_URL = "/v1/system/security/fips"
DEPOT_URL = "v1/system/settings/depot"
SDDC_MANAGER_URL = "v1/sddc-managers"
CREDENTIALS_URL = "v1/credentials"
USERS_URL = "v1/users"
ROLES_URL = "v1/roles"
SSO_DOMAINS_URL = "v1/sso-domains"
PROXY_URL = "v1/system/proxy-configuration"

LOCAL_NTP_URL = "http://localhost/appliancemanager/ntp/configuration"
LOCAL_DNS_URL = "http://localhost/appliancemanager/dns/configuration"

# Task
TASKS = "inventory/tasks"
TASK_BY_ID = "v1/tasks/{0}"

# SDDC manager reference version
SDDC_MANAGER_VERSION_4_5_0_0 = "4.5.0.0"
