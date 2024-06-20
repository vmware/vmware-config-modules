# Run the control functional validations from your local dev laptop

###### Set up sshuttle to tunnel ssl calls to SDDC. Replace jump_host_ip_address with your actual vcf Linux Jump host IP address and replace subnets with your actual subnets. 


sudo sshuttle --no-latency-control -r root@jump_host_ip_address subnets --ssh-cmd 'ssh' --python=/usr/bin/python2.7

###### Set up python virtual env
   

`python3 -m venv venv`
   

`source venv/bin/activate`
   

`pip install -r requirements/functional-test-requirements.txt`
   

###### Set up SDDC Manager SSO admin credentials environment variables for the SDDC instance to test with. 
The test script will fetch other appliance credentials automatically using sddc manager credential API
   
   
`export SM_HOST=SDDC_Manager_Host_IP_Address`


`export SM_USERNAME=SDDC_Manager_Admin_sso_user_name`


`export SM_PASSWORD=SDDC_Manager_Password`

   
###### Perform functional testing using SDDC instance. Use custom pytest commandline options below:
   
   a) --include_list=INCLUDE_LIST
   
        include list for controls. The query syntax: --include_list 'product1:[comma separated control list] or product2:[comma separated control list] or ...'
   
        For example: --include_list 'vcenter:ntp,dns,syslog or sddc_manager:ntp,dns'
   
        when '--include_list' is not specified it takes all controls for all product except the controls in exclude_list. when [comma separated control list] is empty it includes all controls from that product.
   
   b) --exclude_list=EXCLUDE_LIST
   
        exclude list for controls. The query syntax: --exclude_list 'product:[comma separated control list] or product:[comma
         separated control list] or ...' For example: --exclude_list 'vcenter:ntp,dns or sddc_manager:ntp'
   
   c) --compliance_values=COMPLIANCE_VALUES
   
        compliance values yaml file path
   
   d) --drift_values=DRIFT_VALUES
   
        drift values yaml file path
   
   e) --rollback=ROLLBACK
   
        boolean - true or false for rolling back the changes 
   

   Examples:

   A) Test syslog control of vcenter

 
`python3 -m pytest functional_tests/central_test -s  --include_list 'vcenter:syslog'  --rollback true --compliance_values  functional_tests/values/sample_nimbus_compliance_values.yaml --drift_values  functional_tests/values/sample_nimbus_drift_values.yaml
`

   B) Test syslog and ntp controls of vcenter


`python3 -m pytest functional_tests/central_test -s  --include_list 'vcenter:syslog,ntp'  --rollback true --compliance_values  functional_tests/values/sample_nimbus_compliance_values.yaml --drift_values  functional_tests/values/sample_nimbus_drift_values.yaml
`

   C) Test all controls for all products


`python3 -m pytest functional_tests/central_test -s --rollback true --compliance_values  functional_tests/values/sample_nimbus_compliance_values.yaml --drift_values  functional_tests/values/sample_nimbus_drift_values.yaml
`

   D) Test all vcenter controls

  
`python3 -m pytest functional_tests/central_test -s  --include_list 'vcenter:'  --rollback true --compliance_values  functional_tests/values/sample_nimbus_compliance_values.yaml --drift_values  functional_tests/values/sample_nimbus_drift_values.yaml
`

   E) Test All vcenter controls except vcenter syslog and ntp and all sddc_manager controls except dns

 
`python3 -m pytest functional_tests/central_test -s  --include_list 'vcenter: or sddc_manager:'  --exclude_list 'vcenter:syslog,ntp or sddc_manager:dns' --rollback true --compliance_values  functional_tests/values/sample_nimbus_compliance_values.yaml --drift_values  functional_tests/values/sample_nimbus_drift_values.yaml
`

# Use jenkins job to start the integration_tests in linux jump host of a VCF instance

1. Create a new jenkins job project
2. Add Build parameters:
   
   LINUX_JUMP_IP - SDDC Linux Jump host IP address
   
   LINUX_JUMP_PASSWORD - SDDC Linux Jump host password
   
   SM_USERNAME - SDDC manager user name
   
   SM_PASSWORD - SDDC manager password
   
   SM_HOST - SDDC manager host IP address
   
   PYTHON_VERSION - Python Version

   BRANCH - Config-Modules Git repo branch name
   
   INCLUDE_LIST - List of controls to be included in the test
   
   EXCLUDE_LIST - List of controls to be excluded from the test
   
   compliance_values - control compliance values yaml file
   
   drift_values - control drift values yaml file
   
   Rollback - Roll back the changes made to the control at the end of the test

   include_list, exclude_list, compliance_values, drift_values and Rollback build parameter will be passed onto pytest 
   commandline options below.
   
   --include_list=INCLUDE_LIST
   
     include list for controls. The query syntax is: --include_list 'product1:[comma separated control list] or product2:[comma separated control list] or ...'
     For example: --include_list 'vcenter:ntp,dns,syslog or sddc_manager:ntp,dns'
     when '--include_list' is not specified it takes all controls for all product except the controls in exclude_list.
     when [comma separated control list] is empty it includes all controls from that product.
   
   --exclude_list=EXCLUDE_LIST
     exclude list for controls. The query syntax: --exclude_list 'product:[comma separated control list] or product:[comma separated control list] or ...'
     For example: --exclude_list 'vcenter:ntp,dns or sddc_manager:ntp'
   
   --compliance_values=COMPLIANCE_VALUES
     compliance values yaml file path
   
   --drift_values=DRIFT_VALUES
     drift values yaml file path

   --rollback=ROLLBACK   
     boolean - true or false for rolling back the changes 
   
3) Add Build Triggers
   
   a) Trigger builds remotely with HTTP post
   
   b) Build periodically
   
   c) By Git code push event
   
4) Build Environment
   a) Select option: Delete workspace before the build starts
   
   b) Set Build Name: #${BUILD_NUMBER} - ${BUILD_USER_ID}
   
   c) Select option: Set jenkins user build variables
   
5) Set up Source Code Management under tab - Source Code Management
   
   1) Set up Repository URL
      
   2) Set up deployment with ssh key in config-module git repo
      
   3) Set up deployment credential in Jenkins with the ssh private key used in step 2) above
    
6) Add shell command for Build step with scripts
   
   chmod u+x ./config-modules/functional_tests/jenkins/build.sh
   
   ./config-modules/functional_tests/jenkins/build.sh
   
   chmod u+x ./config-modules/functional_tests/jenkins/remote_test_script.sh
   
   ./config-modules/functional_tests/jenkins/remote_test_script.sh
   
7) Publish HTML report as Post-build Actions
   
   Set HTML directory to archive to: test_result/$BUILD_ID
   
   Set Index page[s] to: functional_test.html
   
   set Report title to HTML Report
   
8) The jenkins job can be invoked remotely from the tests script from another pipeline
   
9) All Credentials will be passed in the environment variables to the integration test script in the jump host integration tests.
   
