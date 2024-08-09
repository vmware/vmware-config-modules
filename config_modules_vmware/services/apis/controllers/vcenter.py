# Copyright 2024 Broadcom. All Rights Reserved.
import logging

from fastapi import APIRouter
from fastapi import Body
from fastapi.encoders import jsonable_encoder
from starlette import status
from starlette.responses import JSONResponse
from typing_extensions import Annotated

from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.auth.contexts.vc_context import VcenterContext
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter
from config_modules_vmware.framework.models.controller_models.metadata import ControllerMetadata
from config_modules_vmware.framework.models.output_models.compliance_response import ComplianceStatus
from config_modules_vmware.framework.models.output_models.configuration_drift_response import Status
from config_modules_vmware.framework.models.output_models.get_current_response import GetCurrentConfigurationStatus
from config_modules_vmware.framework.utils import utils
from config_modules_vmware.interfaces.controller_interface import ControllerInterface
from config_modules_vmware.services.apis.controllers.consts import VC_GET_CONFIGURATION_V1
from config_modules_vmware.services.apis.controllers.consts import VC_SCAN_DRIFTS_V1
from config_modules_vmware.services.apis.models.drift_payload import DriftResponsePayload
from config_modules_vmware.services.apis.models.error_model import Error
from config_modules_vmware.services.apis.models.error_model import ErrorSource
from config_modules_vmware.services.apis.models.error_model import Message
from config_modules_vmware.services.apis.models.get_config_payload import GetConfigResponsePayload
from config_modules_vmware.services.apis.models.get_config_payload import GetConfigStatus
from config_modules_vmware.services.apis.models.openapi_examples import get_config_vc_request_payload_invalid_example
from config_modules_vmware.services.apis.models.openapi_examples import (
    get_config_vc_request_payload_with_template_example,
)
from config_modules_vmware.services.apis.models.openapi_examples import (
    get_config_vc_request_payload_without_template_example,
)
from config_modules_vmware.services.apis.models.openapi_examples import scan_drift_vc_200_response_example
from config_modules_vmware.services.apis.models.openapi_examples import scan_drift_vc_500_response_example
from config_modules_vmware.services.apis.models.openapi_examples import scan_drift_vc_request_payload_example
from config_modules_vmware.services.apis.models.request_payload import GetConfigurationRequest
from config_modules_vmware.services.apis.models.request_payload import ScanDriftsRequest
from config_modules_vmware.services.apis.models.target_model import AuthType
from config_modules_vmware.services.apis.models.target_model import RequestTarget
from config_modules_vmware.services.apis.models.target_model import Target

logger = LoggerAdapter(logging.getLogger(__name__))
vcenter_router = APIRouter()


def _create_vcenter_get_config_exception(hostname: str, error_message: str) -> GetConfigResponsePayload:
    """
    Create a vcenter get config exception.
    :param hostname: the hostname of the vcenter.
    :type str: str
    :param error_message: the error message.
    :type str: str
    :return: get config response payload with error information.
    :rtype: GetConfigResponsePayload
    """
    current_time = utils.get_current_time()
    return jsonable_encoder(
        GetConfigResponsePayload(
            description="Exception fetching configuration.",
            status=GetCurrentConfigurationStatus.FAILED,
            timestamp=current_time,
            target=Target(type=BaseContext.ProductEnum.VCENTER, hostname=hostname),
            errors=[
                Error(
                    timestamp=current_time,
                    source=ErrorSource(endpoint=VC_GET_CONFIGURATION_V1),
                    error=Message(message=error_message),
                )
            ],
        ),
        exclude_none=True,
    )


def _create_vcenter_drift_exception(hostname: str, error_message: str) -> DriftResponsePayload:
    """
    Create a vcenter drift exception.
    :param hostname: the hostname of the vcenter.
    :type str: str
    :param error_message: the error message.
    :type str: str
    :return: drift response payload with error information.
    :rtype: DriftResponsePayload
    """
    current_time = utils.get_current_time()
    return jsonable_encoder(
        DriftResponsePayload(
            description="Exception fetching drifts.",
            status=Status.FAILED,
            timestamp=current_time,
            target=Target(type=BaseContext.ProductEnum.VCENTER, hostname=hostname),
            errors=[
                Error(
                    timestamp=current_time,
                    source=ErrorSource(endpoint=VC_SCAN_DRIFTS_V1),
                    error=Message(message=error_message),
                )
            ],
        ),
        exclude_none=True,
    )


def _get_vcenter_context(target: RequestTarget) -> VcenterContext:
    """
    Creates a VCenterContext object from the incoming request payload.
    :param target: the vcenter target object
    :type target: Target
    :return: vcenter context object
    :rtype: VcenterContext
    :raise Exception: missing credentials
    """
    for auth in target.auth:
        if auth.type == AuthType.SSO:
            if auth.username and auth.password:
                if auth.ssl_thumbprint:
                    # Use ssl thumbprint if provided in request payload
                    return VcenterContext(target.hostname, auth.username, auth.password, auth.ssl_thumbprint)
                # Use cert directory if no thumbprint
                return VcenterContext(target.hostname, auth.username, auth.password, verify_ssl=True)
            else:
                raise Exception("Missing vcenter required product credentials")
    raise Exception(f"SSO auth missing for vcenter {target.hostname}")


@vcenter_router.post(
    path=VC_GET_CONFIGURATION_V1,
    response_description="The filtered configuration spec.",
    response_model=GetConfigResponsePayload,
)
def get_configuration(
    get_configuration_request: Annotated[
        GetConfigurationRequest,
        Body(
            openapi_examples={
                "default": get_config_vc_request_payload_without_template_example,
                "template": get_config_vc_request_payload_with_template_example,
                "invalid": get_config_vc_request_payload_invalid_example,
            }
        ),
    ]
) -> JSONResponse:
    """Endpoint to get vcenter configuration."""
    hostname = get_configuration_request.target.hostname
    logger.info(f"Getting vcenter configuration for {hostname}")

    try:
        vcenter_context = _get_vcenter_context(get_configuration_request.target)
    except Exception as e:
        logger.error(e)
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_create_vcenter_get_config_exception(hostname, str(e)),
        )

    try:
        controller_interface = ControllerInterface(vcenter_context)
        configuration = controller_interface.get_current_configuration(
            controller_type=ControllerMetadata.ControllerType.CONFIGURATION, template=get_configuration_request.template
        )
        if configuration is None:
            raise TypeError("Retrieved configuration is None.")
        # missing status in configuration response
        workflow_status = configuration.get(consts.STATUS)
        if workflow_status is None:
            raise KeyError("Missing status in configuration response.")

        # error in get configuration workflow
        if workflow_status == GetCurrentConfigurationStatus.ERROR:
            raise Exception(configuration.get(consts.MESSAGE))

        # success, skipped, partial, failed in get configuration workflow
        current_time = utils.get_current_time()
        return_response = GetConfigResponsePayload(
            status=GetConfigStatus.SUCCESS,
            timestamp=current_time,
            target=Target(type=BaseContext.ProductEnum.VCENTER, hostname=hostname),
        )
        status_code = status.HTTP_200_OK
        if workflow_status == GetCurrentConfigurationStatus.PARTIAL:
            return_response.status = GetConfigStatus.PARTIAL
        elif (
            workflow_status == GetCurrentConfigurationStatus.FAILED
            or workflow_status == GetCurrentConfigurationStatus.SKIPPED
        ):
            return_response.status = GetConfigStatus.FAILED
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        if configuration.get(consts.MESSAGE) is not None:
            return_response.errors = [
                Error(
                    timestamp=current_time,
                    source=ErrorSource(endpoint=VC_GET_CONFIGURATION_V1),
                    error=Message(message=configuration.get(consts.MESSAGE)),
                )
            ]
        if configuration.get(consts.RESULT) is not None:
            return_response.result = configuration.get(consts.RESULT)
        return JSONResponse(status_code=status_code, content=jsonable_encoder(return_response, exclude_none=True))
    except Exception as e:
        logger.error(e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_create_vcenter_get_config_exception(hostname, str(e)),
        )


@vcenter_router.post(
    path=VC_SCAN_DRIFTS_V1,
    response_model=DriftResponsePayload,
    responses={200: scan_drift_vc_200_response_example, 500: scan_drift_vc_500_response_example},
)
def scan_drifts(
    scan_drifts_request: Annotated[
        ScanDriftsRequest, Body(openapi_examples={"default": scan_drift_vc_request_payload_example})
    ]
) -> JSONResponse:
    """Endpoint to get drifts against an input spec."""
    logger.info(f"Scan drifts initiated for {scan_drifts_request.target.hostname}")

    try:
        vcenter_context = _get_vcenter_context(scan_drifts_request.target)
    except Exception as e:
        logger.error(e)
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_create_vcenter_drift_exception(scan_drifts_request.target.hostname, str(e)),
        )

    try:
        controller_interface = ControllerInterface(vcenter_context)
        drift_response = controller_interface.check_compliance(
            controller_type=ControllerMetadata.ControllerType.CONFIGURATION,
            desired_state_spec=scan_drifts_request.input_spec,
        )
        if drift_response is None:
            raise TypeError("Drift response is None.")
        # missing status in drift response
        workflow_status = drift_response.get(consts.STATUS)
        if workflow_status is None:
            raise KeyError("Missing status in drift response.")
        # error in compliance workflow
        if workflow_status == ComplianceStatus.ERROR:
            raise Exception(drift_response.get(consts.MESSAGE))

        # mapping configuration drift response to API drift response spec. Currently, they are the same.
        try:
            if consts.CHANGES in drift_response:
                drift_response = drift_response.get(consts.CHANGES)
            elif consts.MESSAGE in drift_response:
                drift_response = drift_response.get(consts.MESSAGE)
            drift_response = jsonable_encoder(DriftResponsePayload(**drift_response), exclude_none=True)
        except Exception as e:
            logger.error(f"Invalid field in drift response {drift_response}")
            raise e

        if workflow_status == ComplianceStatus.FAILED:
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=drift_response)
        else:
            return JSONResponse(status_code=status.HTTP_200_OK, content=drift_response)
    except Exception as e:
        logger.error(e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_create_vcenter_drift_exception(scan_drifts_request.target.hostname, str(e)),
        )
