# Copyright 2024 Broadcom. All Rights Reserved.

CONFIG_MODULES = "/config-modules"
CONFIG_MODULES_API = CONFIG_MODULES + "/api"

# vcenter endpoints
VC_GET_CONFIGURATION_V1 = CONFIG_MODULES_API + "/vcenter/configuration/v1/get"
VC_SCAN_DRIFTS_V1 = CONFIG_MODULES_API + "/vcenter/configuration/v1/scan-drifts"

# misc endpoints
ABOUT_ENDPOINT = CONFIG_MODULES + "/about"
DOCS_ENDPOINT = CONFIG_MODULES + "/docs"
REDOC_ENDPOINT = CONFIG_MODULES + "/redoc"
HEALTH_ENDPOINT = CONFIG_MODULES + "/health"
