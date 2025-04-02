import logging
import socket
import ssl
from typing import Any

from config_modules_vmware.framework.auth.ssl.cert_info import CertInfo
from config_modules_vmware.framework.clients.common import consts
from config_modules_vmware.framework.logging.logger_adapter import LoggerAdapter

logger = LoggerAdapter(logging.getLogger(__name__))


def validate_all_certificates(hostname, certificate_list) -> tuple[ssl.SSLContext, Any]:
    """
    Checks if any of the CertInfo's passed in the certificate_list or the default CA Certificates are valid for
        the provided hostname.
    First checks all certificates as a whole, if it is successful, no further processing is needed and the context
        is returned.
    If the initial connection fails with either an expired certificate or a hostname/ip address mismatch,
        further processing is done to check each of the provided certificates for the enforce_hostname_verification
        or enforce_date_validity_checking flags and try that certificate individually excluding those checks.
        If this is the case the context and the successful certificate are returned.

    :param hostname: hostname to connect to.
    :type hostname: str
    :param certificate_list: List of CertInfo object with the certificate string and enforce hostname/date flags.
    :type certificate_list: list[CertInfo]
    :return: Tuple of SSLContext and successful CertInfo or None.
    :rtype: tuple
    """
    all_cert_strs = _concat_all_cert_strings(certificate_list)
    context = ssl.create_default_context(cadata=all_cert_strs, capath=consts.SSL_VERIFY_CA_PATH)
    context.verify_flags = ssl.VERIFY_X509_PARTIAL_CHAIN  # pylint: disable=E1101
    with socket.create_connection((hostname, 443)) as sock:
        try:
            with context.wrap_socket(sock, server_hostname=hostname) as wrapped_socket:
                wrapped_socket.getpeercert()
                logger.debug("Initial context with all certificates was successful.")
                return context, None
        except ssl.SSLCertVerificationError as e:
            if "certificate has expired" in e.verify_message.lower():
                logger.debug(
                    "Initial context with all certificates failed with certificate expired error. "
                    "Checking all passed in certificates to check for expiration verification override..."
                )
                return _handle_expired_override(hostname, certificate_list)
            elif "hostname mismatch" in e.verify_message.lower():
                logger.debug(
                    "Initial context with all certificates failed with hostname mismatch error. "
                    "Checking all passed in certificates to check for hostname verification override..."
                )
                return _handle_hostname_override(hostname, certificate_list)
            elif "ip address mismatch" in e.verify_message.lower():
                logger.debug(
                    "Initial context with all certificates failed with IP address mismatch error. "
                    "Checking all passed in certificates to check for hostname verification override..."
                )
                return _handle_hostname_override(hostname, certificate_list)
            logger.error(
                f"Certificate verification failed for reasons other than hostname mismatch or date validation. [{e}]"
            )
            raise Exception("No valid certificate found") from e


def _concat_all_cert_strings(certificate_list):
    all_certs = ""
    for certificate in certificate_list:
        all_certs += certificate.certificate_str + "\n"
    return all_certs


def _handle_hostname_override(hostname, certificate_list) -> tuple[ssl.SSLContext, CertInfo]:
    for certificate in certificate_list:
        if not certificate.enforce_hostname_verification:
            context = _get_valid_ssl_context(hostname, certificate)
            if context:
                logger.debug(
                    "Found certificate with hostname verification disabled and successfully connected to target."
                )
                return context, certificate
    logger.error("No individual certificate configurations were successful in handling the hostname mismatch.")
    raise Exception("No valid certificate found")


def _handle_expired_override(hostname, certificate_list) -> tuple[ssl.SSLContext, CertInfo]:
    for certificate in certificate_list:
        if not certificate.enforce_date_validity_checking:
            context = _get_valid_ssl_context(hostname, certificate)
            if context:
                logger.debug(
                    "Found certificate with expiration verification disabled and successfully connected to target."
                )
                return context, certificate
    logger.error("No individual certificate configurations were successful in handling the invalid certificate date.")
    raise Exception("No valid certificate found")


def _get_valid_ssl_context(_hostname, _cert_info, cert_reqs=ssl.CERT_REQUIRED):
    context = ssl.create_default_context(cadata=_cert_info.certificate_str)
    context.verify_flags = ssl.VERIFY_X509_PARTIAL_CHAIN  # pylint: disable=E1101
    if cert_reqs == ssl.CERT_NONE:
        context.check_hostname = False
        context.verify_mode = cert_reqs
    else:
        context.check_hostname = _cert_info.enforce_hostname_verification

    with socket.create_connection((_hostname, 443)) as sock:
        try:
            with context.wrap_socket(sock, server_hostname=_hostname) as wrapped_socket:
                wrapped_socket.getpeercert()
                return context
        except ssl.SSLCertVerificationError as e:
            if (
                "certificate has expired" in e.verify_message
                and cert_reqs != ssl.CERT_NONE
                and not _cert_info.enforce_date_validity_checking
            ):
                return _get_valid_ssl_context(_hostname, _cert_info, cert_reqs=ssl.CERT_NONE)
            return None
