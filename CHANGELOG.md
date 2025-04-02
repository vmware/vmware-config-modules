# CURRENTLY-IN-DEVELOPMENT
# `v0.16.0.0`
### Framework enhancements
- Removed salt extension as an individual dependent module
### Controller enhancements
- VCSA Controllers
    - Using API for VCSA TLS version compliance check on VCF5.2.
    - Add 5 minutes command timeout for VCSA TLS version on VCF4411.
    - Code refactoring, bug fixes for control users, groups and roles.
### Dependency Version Changes
- pyVmomi version requirement changed to "pyVmomi==8.0.2.0.1."
# `v0.15.0.0`
### New Controllers
- VCSA Controllers
    - 1225 - ip_based_storage_port_group_config
- ESXi Controllers
    - 1114 - snmp_config
    - 4 - ssh_host_based_authentication
    - 7 - ssh_permit_user_environment
    - 16 - ssh_permit_tunnel
    - 13 - ssh_gateway_ports
    - 147 - ntp_config
    - 22 - password_quality_config
    - 12 - ssh_compression
    - 6 - ssh_permit_empty_passwords
    - 11 - ssh_strict_mode
    - 14 - ssh_x11_forwarding
    - 136 - log_location_config
### Controller enhancements
- ESXi Controllers
    - Fix for alarm_esx_remote_syslog_failure by adding check for expression attribute
    - Add version check for rhttpproxy fips 140 esxi control
### Bug Fixes
- Delete vCenter REST session as part of the vc_context `__exit__()`.
- VM migration fix for template vms
# `v0.14.6.0`
##### Released by codydouglasBC on Sept 05, 2024 @ 11:07 PM UTC
### Dependency Version Changes
- lxml version requirement changed to "lxml>=4.9.1,<=5.2.2"
- requests version requirement changed to "requests>=2.31.0"
- pyOpenSSL version requirement changed to "pyOpenSSL>=23.2.0,<=24.0.0"
- urllib3 version requirement changed to "urllib3>=1.26.6,<2.0.0"
# `v0.14.0.0`
##### Released by ravi-pratap-s on Aug 09, 2024 @ 06:33 PM UTC
### New Controllers
- ESXi Controllers
    - 160 - pg_vss_forged_transmits_accept
    - 1121 - syslog_strict_x509_compliance
    - 31 - lockdown_mode
    - 125 - lockdown_mode_exception_users
    - 111 - ssh_service_policy
- VCSA Controllers
    - 417 - dvs_pg_netflow_config
### Controller Enhancements
 - SDDC Manager control 1605 - support remediation for roles to sso users/groups mapping.
### Compliance Control Schema Changes
  - Schema change for users_groups_roles control (1605) for product sddc manager.
# `v0.13.3.0`
##### Released by rjew-bc on Aug 06, 2024 @ 09:15 PM UTC
### Framework Enhancements
- Multi-version support for configuration controls
# `v0.13.2.0`
##### Released by ravi-pratap-s on Jul 30, 2024 @ 08:42 PM UTC
### Dependency Version Changes
  - pyVmomi version downgraded to 7.0.3 inline with salt-ext dependency.
# `v0.13.1.0`
##### Released by codydouglasBC on Jul 24, 2024 @ 10:56 PM UTC
### Bug Fixes
  - Description in setup.py was not formatted properly and blocked publishing to PyPi.
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
