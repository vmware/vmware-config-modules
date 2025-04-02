class CertInfo:
    """
    Class to hold SSL related certificates and settings to be passed to the VCContext.
    Ultimately, the info is used when creating the vc_rest_client.
    """

    def __init__(self, certificate_str=None, enforce_hostname_verification=True, enforce_date_validity_checking=True):
        """
        Initialize CertInfo to be used in the SSLContext when opening a REST client.
        """
        self._certificate_str = certificate_str
        self._enforce_hostname_verification = enforce_hostname_verification
        self._enforce_date_validity_checking = enforce_date_validity_checking

    @property
    def certificate_str(self) -> str:
        return self._certificate_str

    @property
    def enforce_hostname_verification(self) -> bool:
        return self._enforce_hostname_verification

    @property
    def enforce_date_validity_checking(self) -> bool:
        return self._enforce_date_validity_checking
