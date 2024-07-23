# CURRENTLY-IN-DEVELOPMENT
# `v0.13.0.0`
##### Released by codydouglasBC on Jul 23, 2024 @ 10:32 PM UTC
### New Controllers
  - ESXi Controllers
    - 105 - firewall_default_action_incoming
    - 106 - firewall_default_action_outgoing
    - 137 - ad_esx_admin_group_config
    - 161 - pg_vss_mac_change_accept
    - 162 - pg_vss_allow_promiscuous_mode
    - 164 - remote_log_server_config
    - 1115 - syslog_enforce_ssl_certificates
    - 1116 - vim_api_session_timeout
    - 1117 - rhttpproxy_fips_140_2_crypt_config
    - 1122 - userworld_memory_zeroing_config
    - 124 - ssh_daemon_login_banner
  - VCSA Controllers
    - 0000 - managed_object_browser
### Controller Enhancements
  - VCSA control 1234 - continue remediation when hitting error on one VM.
  - SDDC Manager control 1604 - remove host and port parameters.
### Dependency Version Changes
  - urllib3 pinned to 1.26.19
# Initial Open Source Release!
- Support for two controller types (Compliance and Configuration)
  - Compliance has support for 5 products and 77 Controllers
    - ESXi - 19 Controllers
    - NSX-T - 1 Controller
    - SDDC Manager - 9 Controllers
    - VCSA - 47 Controllers
    - VRSLCM - 1 Controller
  - Configuration has support for 2 VC Profile components - AuthManagement and Appliance.
