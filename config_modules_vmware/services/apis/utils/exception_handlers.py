from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from config_modules_vmware.framework.models.output_models.configuration_drift_response import Status
from config_modules_vmware.framework.models.output_models.get_current_response import GetCurrentConfigurationStatus
from config_modules_vmware.framework.utils import utils
from config_modules_vmware.services.apis.controllers.consts import VC_GET_CONFIGURATION_V1
from config_modules_vmware.services.apis.controllers.consts import VC_GET_SCHEMA_V1
from config_modules_vmware.services.apis.controllers.consts import VC_SCAN_DRIFTS_V1
from config_modules_vmware.services.apis.controllers.consts import VC_VALIDATE_CONFIGURATION_V1
from config_modules_vmware.services.apis.models import schema_payload
from config_modules_vmware.services.apis.models import validate_payload
from config_modules_vmware.services.apis.models.drift_payload import DriftResponsePayload
from config_modules_vmware.services.apis.models.error_model import Error
from config_modules_vmware.services.apis.models.error_model import ErrorSource
from config_modules_vmware.services.apis.models.error_model import Message
from config_modules_vmware.services.apis.models.get_config_payload import GetConfigResponsePayload
from config_modules_vmware.services.apis.models.schema_payload import SchemaResponsePayload
from config_modules_vmware.services.apis.models.target_model import Target
from config_modules_vmware.services.apis.models.validate_payload import ValidateResponsePayload


def create_vcenter_get_config_exception(hostname: str, error_message: str) -> GetConfigResponsePayload:
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
    return GetConfigResponsePayload(
        description="Exception fetching configuration.",
        status=GetCurrentConfigurationStatus.FAILED,
        timestamp=current_time,
        target=Target(type=BaseContext.ProductEnum.VCENTER, hostname=hostname) if hostname else None,
        errors=[
            Error(
                timestamp=current_time,
                source=ErrorSource(endpoint=VC_GET_CONFIGURATION_V1),
                error=Message(message=error_message),
            )
        ],
    )


def create_vcenter_drift_exception(hostname: str, error_message: str) -> DriftResponsePayload:
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
    return DriftResponsePayload(
        description="Exception fetching drifts.",
        status=Status.FAILED,
        timestamp=current_time,
        target=Target(type=BaseContext.ProductEnum.VCENTER, hostname=hostname) if hostname else None,
        errors=[
            Error(
                timestamp=current_time,
                source=ErrorSource(endpoint=VC_SCAN_DRIFTS_V1),
                error=Message(message=error_message),
            )
        ],
    )


def create_vcenter_schema_exception(hostname: str, error_message: str) -> SchemaResponsePayload:
    """
    Create a vcenter schema exception.
    :param hostname: the hostname of the vcenter.
    :type str: str
    :param error_message: the error message.
    :type str: str
    :return: schema response payload with error information.
    :rtype: DriftResponsePayload
    """
    current_time = utils.get_current_time()
    return SchemaResponsePayload(
        description="Exception fetching schema.",
        status=schema_payload.Status.FAILED,
        timestamp=current_time,
        target=Target(type=BaseContext.ProductEnum.VCENTER, hostname=hostname) if hostname else None,
        errors=[
            Error(
                timestamp=current_time,
                source=ErrorSource(endpoint=VC_GET_SCHEMA_V1),
                error=Message(message=error_message),
            )
        ],
    )


def create_vcenter_validate_exception(hostname: str, error_message: str) -> ValidateResponsePayload:
    """
    Create a vcenter validate exception.
    :param hostname: the hostname of the vcenter.
    :type str: str
    :param error_message: the error message.
    :type str: str
    :return: validate response payload with error information.
    :rtype: ValidateResponsePayload
    """
    current_time = utils.get_current_time()
    return ValidateResponsePayload(
        description="Exception validating configuration.",
        status=validate_payload.Status.FAILED,
        timestamp=current_time,
        target=Target(type=BaseContext.ProductEnum.VCENTER, hostname=hostname) if hostname else None,
        errors=[
            Error(
                timestamp=current_time,
                source=ErrorSource(endpoint=VC_VALIDATE_CONFIGURATION_V1),
                error=Message(message=error_message),
            )
        ],
    )
