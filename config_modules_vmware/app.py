# Copyright 2024 Broadcom. All Rights Reserved.
import logging.config
import os

import yaml
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from config_modules_vmware.services.apis.controllers.consts import DOCS_ENDPOINT
from config_modules_vmware.services.apis.controllers.consts import REDOC_ENDPOINT
from config_modules_vmware.services.apis.controllers.misc import misc_router
from config_modules_vmware.services.apis.controllers.vcenter import vcenter_router
from config_modules_vmware.services.config import Config


def custom_openapi():
    """This creates the openapi specification file using FastAPI utilities."""
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Config-modules APIs",
        version="1.0.0",
        summary="List of APIs exposed by Config-modules",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


def setup_logging():
    """This sets up logging configuration that is applicable when run both through gunicorn and as FastAPI server."""
    log_config_path = os.path.join(os.path.dirname(__file__), "log_config.yml")
    with open(log_config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
        # Set file handler config using app config
        logging_variables = Config.get_section("service.logging.file")
        log_dir = os.environ.get("CONFIG_MODULES_DOCKER_LOG_DIR", logging_variables.get("LogFileDir"))
        os.makedirs(log_dir, exist_ok=True)
        config["handlers"]["file"]["filename"] = os.path.join(log_dir, logging_variables.get("FileName"))
        config["handlers"]["file"]["maxBytes"] = logging_variables.getint("FileSize")
        config["handlers"]["file"]["backupCount"] = logging_variables.getint("MaxCount")
        config["handlers"]["file"]["level"] = logging_variables.get("LogLevel")

        # Set log level for default handler
        logging_variables = Config.get_section("service.logging.console")
        config["handlers"]["default"]["level"] = logging_variables.get("LogLevel")

        logging.config.dictConfig(config)


# Start the app and register routes
app = FastAPI(title="Config Modules", docs_url=DOCS_ENDPOINT, redoc_url=REDOC_ENDPOINT)
app.include_router(misc_router, tags=["misc"])
app.include_router(vcenter_router, tags=["vcenter"])
app.openapi = custom_openapi
setup_logging()
