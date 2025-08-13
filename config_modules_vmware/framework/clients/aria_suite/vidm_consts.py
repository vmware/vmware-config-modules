# Copyright 2023-2024 VMware, Inc.  All rights reserved. -- VMware Confidential

# VIDM REST API
VIDM_API_BASE = "https://{}/"
VIDM_TOKEN_URL = VIDM_API_BASE + "SAAS/auth/oauthtoken"
VIDM_REST_API_TIMEOUT_VALUE = 30
VIDM_ACCESS_TOKEN = "accessToken"  # nosec

RULESETS_URL = VIDM_API_BASE + "acs/rulesets"
RULESET_ASSOCIATIONS_URL = VIDM_API_BASE + "acs/associations/rulesets/{}"
SCIM_GROUPS_URL = VIDM_API_BASE + "SAAS/jersey/manager/api/scim/Groups/"
SCIM_USERS_URL = VIDM_API_BASE + "SAAS/jersey/manager/api/scim/Users/"
ROLE_URL = VIDM_API_BASE + "SAAS/jersey/manager/api/scim/Roles/"
