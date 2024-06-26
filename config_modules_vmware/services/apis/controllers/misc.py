# Copyright 2024 Broadcom. All Rights Reserved.
import logging

from fastapi import APIRouter

from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.services.apis.controllers.consts import ABOUT_ENDPOINT
from config_modules_vmware.services.apis.controllers.consts import HEALTH_ENDPOINT
from config_modules_vmware.services.apis.models.about import About
from config_modules_vmware.services.apis.models.healthcheck import HealthCheck

logger = LoggerAdapter(logging.getLogger(__name__))
misc_router = APIRouter()


@misc_router.get(ABOUT_ENDPOINT, response_model=About)
def about() -> dict:
    """API to retrieve package information."""
    logger.info("Getting information about package.")
    return About.__dict__


@misc_router.get(HEALTH_ENDPOINT, response_model=HealthCheck)
def health() -> HealthCheck:
    """API to retrieve health status."""
    logger.info("Getting health status.")
    return HealthCheck(status="OK")
