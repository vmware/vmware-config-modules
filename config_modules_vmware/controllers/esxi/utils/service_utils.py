# Copyright 2024 Broadcom. All Rights Reserved.
import logging

from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter

logger = LoggerAdapter(logging.getLogger(__name__))

SERVICE_RUNNING = "service_running"
SERVICE_POLICY = "service_policy"


class HostServiceUtil:
    def __init__(self, host_service):
        """
        :param host_service: Host service object
        :typpe host_service: vim.host.ServiceSystem
        """
        self.host_service = host_service
        self.service_map = self._build_service_map()

    def _build_service_map(self):
        service_map = {}
        for service in self.host_service.serviceInfo.service:
            service_map[service.key] = service
        return service_map

    def get_service_status(self, service_name):
        """
        Query ESXi config manager service system for specific service status
        :param service_name: service name
        :type service_name: str
        :return: Dict of service status and possible errors
        """
        errors = []
        service_status = {}
        service = self.service_map.get(service_name, None)
        if service is None:
            errors.append("service not found")
        else:
            service_status = {SERVICE_RUNNING: service.running, SERVICE_POLICY: service.policy}
        return service_status, errors

    def start_stop_service(self, service_name, service_running):
        """
        Start/stop ESXi service by config manager service system for specific service
        :param service_name: service name
        :type service_name: str
        :param service_running: desired service running status
        :type service_running: boolean
        """
        if not service_running:
            self.host_service.StopService(id=service_name)
        else:
            self.host_service.StartService(id=service_name)

    def update_service_policy(self, service_name, service_policy):
        """
        Update ESXi service policy by config manager service system for specific service
        :param service_name: service name
        :type service_name: str
        :param service_policy: desired service policy
        :type service_policy: string of ("on", "off")
        :return: Tuple of service status and possible errors
        """
        # update service policy based on desired state
        self.host_service.UpdateServicePolicy(id=service_name, policy=service_policy)
