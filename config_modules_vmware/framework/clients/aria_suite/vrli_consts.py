
INSTALL_LI_AGENT_SCRIPT = '''#!/bin/bash
# Installs and configures vRLI agent
# Arguments: vRLI cluster address; the port for vRLI HTTP endpoint
VRLI_CLUSTER="$1"
wget https://$VRLI_CLUSTER:9543/api/v1/agent/packages/types/rpm --no-check-certificate -O /tmp/li-agent.rpm
chmod +x /tmp/li-agent.rpm
rpm -Uvh /tmp/li-agent.rpm
cat <<EOF > /var/lib/loginsight-agent/liagent.ini
; VMware LogInsight Agent configuration is adapted to SDDC Manager VM logging needs. Do not modify it.

[server]
; Hostname or IP address of your Log Insight server / cluster load balancer. Default:
hostname=$VRLI_CLUSTER

; Protocol can be cfapi (Log Insight REST API), syslog. Default:
proto=cfapi

; Log Insight server port to connect to. Default ports for protocols (all TCP):
; syslog: 514; syslog with ssl: 6514; cfapi: 9000; cfapi with ssl: 9543. Default:
port=9000

; SSL usage. Default:
ssl=no
; Example of configuration with trusted CA:
ssl=no
;ssl_ca_path=/etc/pki/tls/certs/ca.pem

; Time in minutes to force reconnection to the server.
; This option mitigates imbalances caused by long-lived TCP connections. Default:
;reconnect=30

[logging]
; Logging verbosity: 0 (no debug messages), 1 (essentials), 2 (verbose with more impact on performance).
; This option should always be 0 under normal operating conditions. Default:
;debug_level=0

[storage]
; Max local storage usage limit (data + logs) in MBs. Valid range: 100-2000 MB.
;max_disk_buffer=200

; Uncomment the appropriate section to collect system logs
; The recommended way is to enable the Linux content pack from LI server
;[filelog|syslog]
;directory=/var/log
;include=messages;messages.?;syslog;syslog.?

[update]
; Do not change this parameter
package_type=bin


; Enable automatic update of the agent. If enabled:
; the agent will silently check for updates from the server and
; if available will automatically download and apply the update.
;auto_update=yes

[filelog|lighttpd]
directory=/opt/vmware/var/log/lighttpd
include=access.log;error.log
event_marker=^\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}
tags={"vmw_product":"vcf", "vcf_component":"lighttpd"}

[filelog|vami]
directory=/opt/vmware/var/log/vami
include=vami-ovf.log;vami.log;vami-sfcb.log
event_marker=^\d{2}\/\d{2}\/\d{4}\s\d{2}:\d{2}:\d{2}
tags={"vmw_product":"vcf", "vcf_component":"vami"}

[filelog|sddc-support]
directory=/opt/vmware/sddc-support
include=compile.log
tags={"vmw_product":"vcf", "vcf_component":"sddc-support"}

[filelog|loginsight-agent]
directory=/var/log/loginsight-agent
include=liagent*.log;liupdater*.log
event_marker=^\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}
tags={"vmw_product":"vcf", "vcf_component":"loginsight-agent"}

[filelog|vmware-network]
directory=/var/log
include=vmware-network.*.log
event_marker=^\w{3}\s\w{3}\s\d{1,2}\s\d{2}:\d{2}:\d{2}
tags={"vmw_product":"vcf", "vcf_component":"vmware-network"}

[filelog|audit]
directory=/var/log/audit
include=audit.log
event_marker=^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}
tags={"vmw_product":"vcf", "vcf_component":"audit"}

[filelog|sddc-manager-ui-app]
directory=/var/log/vmware/vcf/sddc-manager-ui-app
include=*.log
event_marker=^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}
tags={"vmw_product":"vcf", "vcf_component":"sddc-manager-ui-app"}

[filelog|lcm]
directory=/var/log/vmware/vcf/lcm
include=*.log
event_marker=^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}
tags={"vmw_product":"vcf", "vcf_component":"lcm"}

[filelog|domainmanager]
directory=/var/log/vmware/vcf/domainmanager
include=*.log
event_marker=^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}
tags={"vmw_product":"vcf", "vcf_component":"domainmanager"}

[filelog|commonsvcs]
directory=/var/log/vmware/vcf/commonsvcs
include=*.log
event_marker=^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}
tags={"vmw_product":"vcf", "vcf_component":"commonsvcs"}

[filelog|operationsmanager]
directory=/var/log/vmware/vcf/operationsmanager
include=*.log
event_marker=^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}
tags={"vmw_product":"vcf", "vcf_component":"operationsmanager"}

[filelog|vmware-vmsvc]
directory=/var/log
include=vmware-vmsvc.log
event_marker=^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}
tags={"vmw_product":"vcf", "vcf_component":"vmware-vmsvc"}

[filelog|auth]
directory=/var/log
include=auth.log
event_marker=^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}
tags={"vmw_product":"vcf", "vcf_component":"auth"}

[filelog|sos]
directory=/var/log
include=sos.log
event_marker=^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}
tags={"vmw_product":"vcf", "vcf_component":"sos"}

EOF
'''