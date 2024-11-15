# CURRENTLY-IN-DEVELOPMENT
# `v0.14.0.1`
### Controller Enhancements
- VCSA Controllers
    - 1230 - Add domain to input for each user in ldap identity source control
    - 1202 - Add vlan range input to support combination of individual VLANs and ranges
    - 1234 - Return partial remediation instead of remediation failed for vm_migrate_encryption control
    - 1234 - Remove "_GLOBAL_" from compliance check output for vm_migrate_encryption control
    - 409 - Exclude offloading enabled switch when remediation and add partial remediation for vc control (network io control)
    - 409 - Removed "_GLOBAL_" on compliance check output on VC network IO control
    - 415 - The vCenter Server users must have the correct roles assigned. (alias)
    - 415 - The vCenter Server users must have the correct roles assigned. (excludes certain roles)
    - 1222 - snmp_v3 (If disabled, shows NON-COMPLIANT. when disabled, should not check additional desired inputs.)
    - 1204 - tlsReconfigurtor (Make tlsv1.2 mandatory for tls control for vcenter)
### Framework Enhancements
    - Use vsphere local domain to fix 404 errors in sso controls by login as AD users
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
