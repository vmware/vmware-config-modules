# ******* WARNING - AUTO GENERATED CODE - DO NOT EDIT *******
from .VmomiSupport import AddBreakingChangesInfo
from .VmomiSupport import AddVersion
from .VmomiSupport import AddVersionParent
from .VmomiSupport import CreateDataType
from .VmomiSupport import CreateEnumType
from .VmomiSupport import CreateManagedType
from .VmomiSupport import dottedVersions
from .VmomiSupport import F_LINK
from .VmomiSupport import F_LINKABLE
from .VmomiSupport import F_OPTIONAL
from .VmomiSupport import F_SECRET
from .VmomiSupport import newestVersions
from .VmomiSupport import oldestVersions
from .VmomiSupport import publicVersions
from .VmomiSupport import stableVersions

# pylint: skip-file

AddVersion("vmodl.version.version0", "", "", 0, "vim25")
AddVersion("sso.version.version3", "sso", "version3", 0, "")
AddVersion("sso.version.version3_1", "sso", "version3_1", 0, "")
AddVersion("sso.version.version3_2", "sso", "version3_2", 0, "")
AddVersion("sso.version.version1_5", "sso", "version1_5", 0, "")
AddVersion("sso.version.version2_5", "sso", "version2_5", 0, "")
AddVersion("sso.version.version1", "sso", "version1", 0, "")
AddVersion("sso.version.version3_5", "sso", "version3_5", 0, "")
AddVersion("sso.version.version2", "sso", "version2", 0, "")
AddVersionParent("vmodl.version.version0", "vmodl.version.version0")
AddVersionParent("sso.version.version3", "vmodl.version.version0")
AddVersionParent("sso.version.version3", "sso.version.version3")
AddVersionParent("sso.version.version3", "sso.version.version1_5")
AddVersionParent("sso.version.version3", "sso.version.version2_5")
AddVersionParent("sso.version.version3", "sso.version.version1")
AddVersionParent("sso.version.version3", "sso.version.version2")
AddVersionParent("sso.version.version3_1", "vmodl.version.version0")
AddVersionParent("sso.version.version3_1", "sso.version.version3")
AddVersionParent("sso.version.version3_1", "sso.version.version3_1")
AddVersionParent("sso.version.version3_1", "sso.version.version1_5")
AddVersionParent("sso.version.version3_1", "sso.version.version2_5")
AddVersionParent("sso.version.version3_1", "sso.version.version1")
AddVersionParent("sso.version.version3_1", "sso.version.version2")
AddVersionParent("sso.version.version3_2", "vmodl.version.version0")
AddVersionParent("sso.version.version3_2", "sso.version.version3")
AddVersionParent("sso.version.version3_2", "sso.version.version3_1")
AddVersionParent("sso.version.version3_2", "sso.version.version3_2")
AddVersionParent("sso.version.version3_2", "sso.version.version1_5")
AddVersionParent("sso.version.version3_2", "sso.version.version2_5")
AddVersionParent("sso.version.version3_2", "sso.version.version1")
AddVersionParent("sso.version.version3_2", "sso.version.version2")
AddVersionParent("sso.version.version1_5", "vmodl.version.version0")
AddVersionParent("sso.version.version1_5", "sso.version.version1_5")
AddVersionParent("sso.version.version1_5", "sso.version.version1")
AddVersionParent("sso.version.version2_5", "vmodl.version.version0")
AddVersionParent("sso.version.version2_5", "sso.version.version1_5")
AddVersionParent("sso.version.version2_5", "sso.version.version2_5")
AddVersionParent("sso.version.version2_5", "sso.version.version1")
AddVersionParent("sso.version.version2_5", "sso.version.version2")
AddVersionParent("sso.version.version1", "vmodl.version.version0")
AddVersionParent("sso.version.version1", "sso.version.version1")
AddVersionParent("sso.version.version3_5", "vmodl.version.version0")
AddVersionParent("sso.version.version3_5", "sso.version.version3")
AddVersionParent("sso.version.version3_5", "sso.version.version3_1")
AddVersionParent("sso.version.version3_5", "sso.version.version3_2")
AddVersionParent("sso.version.version3_5", "sso.version.version1_5")
AddVersionParent("sso.version.version3_5", "sso.version.version2_5")
AddVersionParent("sso.version.version3_5", "sso.version.version1")
AddVersionParent("sso.version.version3_5", "sso.version.version3_5")
AddVersionParent("sso.version.version3_5", "sso.version.version2")
AddVersionParent("sso.version.version2", "vmodl.version.version0")
AddVersionParent("sso.version.version2", "sso.version.version1_5")
AddVersionParent("sso.version.version2", "sso.version.version1")
AddVersionParent("sso.version.version2", "sso.version.version2")

newestVersions.Add("sso.version.version3_5")
stableVersions.Add("sso.version.version3_5")
publicVersions.Add("sso.version.version3_5")
dottedVersions.Add("sso.version.version3_5")
oldestVersions.Add("sso.version.version1")

CreateDataType(
    "sso.AboutInfo",
    "SsoAboutInfo",
    "vmodl.DynamicData",
    "sso.version.version1",
    [
        ("version", "string", "sso.version.version1", 0),
        ("build", "string", "sso.version.version1", 0),
        ("apiRevision", "string", "sso.version.version1", 0),
        ("clusterId", "string", "sso.version.version1", 0),
        ("deploymentId", "string", "sso.version.version1", 0),
        ("ssoProductInfo", "string", "sso.version.version3_1", F_OPTIONAL),
        ("ssoProductVersionMajor", "string", "sso.version.version3_1", F_OPTIONAL),
        ("ssoProductVersionMinor", "string", "sso.version.version3_1", F_OPTIONAL),
        ("ssoProductVersionMaint", "string", "sso.version.version3_1", F_OPTIONAL),
    ],
)
CreateDataType(
    "sso.PrincipalId",
    "SsoPrincipalId",
    "vmodl.DynamicData",
    "sso.version.version1",
    [
        ("name", "string", "sso.version.version1", 0),
        ("domain", "string", "sso.version.version1", 0),
    ],
)
CreateManagedType(
    "sso.SessionManager",
    "SsoSessionManager",
    "vmodl.ManagedObject",
    "sso.version.version1",
    [
        ("defaultLocale", "string", "sso.version.version1", 0, "System.Anonymous"),
        ("supportedLocales", "string[]", "sso.version.version1", 0, "System.Anonymous"),
    ],
    [
        (
            "login",
            "Login",
            "sso.version.version1",
            (),
            (0, "void", "void"),
            "System.Anonymous",
            [
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "logout",
            "Logout",
            "sso.version.version1",
            (),
            (0, "void", "void"),
            "System.Anonymous",
            [
                "vmodl.fault.InvalidRequest",
            ],
        ),
        (
            "setLocale",
            "SetLocale",
            "sso.version.version1",
            (("locale", "string", "sso.version.version1", 0, None),),
            (0, "string", "string"),
            "System.Anonymous",
            None,
        ),
        (
            "getLocale",
            "GetLocale",
            "sso.version.version1",
            (),
            (0, "string", "string"),
            "System.Anonymous",
            None,
        ),
    ],
)
CreateDataType(
    "sso.admin.ActiveDirectoryJoinInfo",
    "SsoAdminActiveDirectoryJoinInfo",
    "vmodl.DynamicData",
    "sso.version.version1_5",
    [
        ("joinStatus", "string", "sso.version.version1_5", 0),
        ("name", "string", "sso.version.version1_5", F_OPTIONAL),
        ("alias", "string", "sso.version.version1_5", F_OPTIONAL),
        ("dn", "string", "sso.version.version3_1", F_OPTIONAL),
    ],
)
CreateEnumType(
    "sso.admin.ActiveDirectoryJoinInfo.JoinStatus",
    "SsoAdminActiveDirectoryJoinInfoJoinStatus",
    "sso.version.version1_5",
    [
        "ACTIVE_DIRECTORY_JOIN_STATUS_UNKNOWN",
        "ACTIVE_DIRECTORY_JOIN_STATUS_WORKGROUP",
        "ACTIVE_DIRECTORY_JOIN_STATUS_DOMAIN",
    ],
)
CreateDataType(
    "sso.admin.AuthenticationAccountInfo",
    "SsoAdminAuthenticationAccountInfo",
    "vmodl.DynamicData",
    "sso.version.version1_5",
    [
        ("userName", "string", "sso.version.version1_5", F_OPTIONAL),
        ("spn", "string", "sso.version.version1_5", F_OPTIONAL),
        ("useMachineAccount", "boolean", "sso.version.version1_5", 0),
    ],
)
CreateDataType(
    "sso.admin.AuthnPolicy",
    "SsoAdminAuthnPolicy",
    "vmodl.DynamicData",
    "sso.version.version3_2",
    [
        ("PasswordAuthnEnabled", "boolean", "sso.version.version3_2", 0),
        ("WindowsAuthEnabled", "boolean", "sso.version.version3_2", 0),
        ("CertAuthEnabled", "boolean", "sso.version.version3_2", 0),
        (
            "clientCertPolicy",
            "sso.admin.ClientCertPolicy",
            "sso.version.version3_2",
            F_OPTIONAL,
        ),
    ],
)
CreateManagedType(
    "sso.admin.CertificateManager",
    "SsoAdminCertificateManager",
    "vmodl.ManagedObject",
    "sso.version.version1",
    None,
    [
        (
            "addCertificate",
            "AddCertificate",
            "sso.version.version1",
            (("certificate", "string", "sso.version.version1", 0, None),),
            (0, "boolean", "boolean"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "getAllCertificates",
            "GetAllCertificates",
            "sso.version.version1",
            (),
            (F_OPTIONAL, "string[]", "string[]"),
            "System.Read",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "findCertificate",
            "FindCertificate",
            "sso.version.version1",
            (("fingerprint", "string", "sso.version.version1", 0, None),),
            (F_OPTIONAL, "string", "string"),
            "System.Read",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "deleteCertificate",
            "DeleteCertificate",
            "sso.version.version1",
            (("fingerprint", "string", "sso.version.version1", 0, None),),
            (0, "boolean", "boolean"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
    ],
)
CreateDataType(
    "sso.admin.ClientCertPolicy",
    "SsoAdminClientCertPolicy",
    "vmodl.DynamicData",
    "sso.version.version3_2",
    [
        ("enabled", "boolean", "sso.version.version3_2", 0),
        ("ocspEnabled", "boolean", "sso.version.version3_2", 0),
        ("useCRLAsFailOver", "boolean", "sso.version.version3_2", 0),
        ("sendOCSPNonce", "boolean", "sso.version.version3_2", 0),
        ("ocspUrl", "string", "sso.version.version3_2", F_OPTIONAL),
        ("ocspResponderSigningCert", "string", "sso.version.version3_2", F_OPTIONAL),
        ("useInCertCRL", "boolean", "sso.version.version3_2", 0),
        ("crlUrl", "string", "sso.version.version3_2", F_OPTIONAL),
        ("crlCacheSize", "int", "sso.version.version3_2", 0),
        ("oids", "string[]", "sso.version.version3_2", F_OPTIONAL),
        ("trustedCAs", "string[]", "sso.version.version3_2", F_OPTIONAL),
    ],
)
CreateManagedType(
    "sso.admin.ComputerManagementService",
    "SsoAdminComputerManagementService",
    "vmodl.ManagedObject",
    "sso.version.version3_1",
    None,
    [
        (
            "getComputers",
            "GetComputers",
            "sso.version.version3_1",
            (("getDCOnly", "boolean", "sso.version.version3_1", 0, None),),
            (0, "sso.admin.VmHost[]", "sso.admin.VmHost[]"),
            "SystemConfiguration.Administrators",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        )
    ],
)
CreateManagedType(
    "sso.admin.ConfigurationManagementService",
    "SsoAdminConfigurationManagementService",
    "vmodl.ManagedObject",
    "sso.version.version1",
    None,
    [
        (
            "getKnownCertificateChains",
            "GetKnownCertificateChains",
            "sso.version.version1",
            (),
            (
                0,
                "sso.admin.ConfigurationManagementService.CertificateChain[]",
                "sso.admin.ConfigurationManagementService.CertificateChain[]",
            ),
            "System.Anonymous",
            [
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "getTrustedCertificates",
            "GetTrustedCertificates",
            "sso.version.version1",
            (),
            (0, "string[]", "string[]"),
            "System.Anonymous",
            [
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "getIssuersCertificates",
            "GetIssuersCertificates",
            "sso.version.version1_5",
            (),
            (0, "string[]", "string[]"),
            "System.Anonymous",
            [
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "importTrustedSTSConfiguration",
            "ImportTrustedSTSConfiguration",
            "sso.version.version2",
            (
                (
                    "stsConfig",
                    "sso.admin.TrustedSTSConfig",
                    "sso.version.version2",
                    0,
                    None,
                ),
            ),
            (0, "void", "void"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
                "sso.admin.fault.ExternalSTSCertChainInvalidTrustedPathFault",
                "sso.admin.fault.ExternalSTSExtraneousCertsInCertChainFault",
            ],
        ),
        (
            "removeTrustedSTSConfiguration",
            "RemoveTrustedSTSConfiguration",
            "sso.version.version2",
            (("issuerName", "string", "sso.version.version2", 0, None),),
            (0, "void", "void"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
                "sso.admin.fault.ExternalSTSCertChainInvalidTrustedPathFault",
                "sso.admin.fault.ExternalSTSExtraneousCertsInCertChainFault",
            ],
        ),
        (
            "importExternalIDPConfiguration",
            "ImportExternalIDPConfiguration",
            "sso.version.version2",
            (("externalIDPConfigDoc", "string", "sso.version.version2", 0, None),),
            (0, "void", "void"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
                "sso.admin.fault.ExternalSTSCertChainInvalidTrustedPathFault",
                "sso.admin.fault.ExternalSTSExtraneousCertsInCertChainFault",
            ],
        ),
        (
            "createExternalIDPConfiguration",
            "CreateExternalIDPConfiguration",
            "sso.version.version3",
            (
                (
                    "config",
                    "sso.admin.IDPConfiguration",
                    "sso.version.version3",
                    0,
                    None,
                ),
            ),
            (0, "void", "void"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.admin.fault.CertChainInvalidTrustedPathFault",
                "sso.admin.fault.ExtraneousCertsInCertChainFault",
            ],
        ),
        (
            "getExternalIDPConfiguration",
            "GetExternalIDPConfiguration",
            "sso.version.version3",
            (("entityID", "string", "sso.version.version3", 0, None),),
            (0, "sso.admin.IDPConfiguration", "sso.admin.IDPConfiguration"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.NotAuthenticated",
                "sso.admin.fault.NoSuchConfigFault",
            ],
        ),
        (
            "setExternalIDPConfiguration",
            "SetExternalIDPConfiguration",
            "sso.version.version3",
            (
                (
                    "config",
                    "sso.admin.IDPConfiguration",
                    "sso.version.version3",
                    0,
                    None,
                ),
            ),
            (0, "void", "void"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.admin.fault.CertChainInvalidTrustedPathFault",
                "sso.admin.fault.ExtraneousCertsInCertChainFault",
            ],
        ),
        (
            "deleteExternalIDPConfiguration",
            "DeleteExternalIDPConfiguration",
            "sso.version.version3",
            (("entityID", "string", "sso.version.version3", 0, None),),
            (0, "void", "void"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.admin.fault.NoSuchConfigFault",
            ],
        ),
        (
            "deleteExternalIDPConfigurationAndUsers",
            "DeleteExternalIDPConfigurationAndUsers",
            "sso.version.version3_5",
            (("entityID", "string", "sso.version.version3_5", 0, None),),
            (0, "void", "void"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.admin.fault.NoSuchConfigFault",
            ],
        ),
        (
            "enumerateExternalIDPEntityIDs",
            "EnumerateExternalIDPEntityIDs",
            "sso.version.version3",
            (),
            (F_OPTIONAL, "string[]", "string[]"),
            "Sso.AdminServer.Administer",
            None,
        ),
        (
            "getExternalIdpTrustedCertificateChains",
            "GetExternalIdpTrustedCertificateChains",
            "sso.version.version2",
            (),
            (
                0,
                "sso.admin.ConfigurationManagementService.CertificateChain[]",
                "sso.admin.ConfigurationManagementService.CertificateChain[]",
            ),
            "System.Anonymous",
            [
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "getExternalIdpTrustedCertificateChain",
            "GetExternalIdpTrustedCertificateChain",
            "sso.version.version2",
            (("entityId", "string", "sso.version.version2", 0, None),),
            (
                0,
                "sso.admin.ConfigurationManagementService.CertificateChain",
                "sso.admin.ConfigurationManagementService.CertificateChain",
            ),
            "System.Anonymous",
            [
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "deleteTrustedCertificate",
            "DeleteTrustedCertificate",
            "sso.version.version1_5",
            (("fingerprint", "string", "sso.version.version1_5", 0, None),),
            (0, "boolean", "boolean"),
            "Sso.AdminServer.Administer",
            [
                "sso.admin.fault.CertificateDeletionFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "setNewSignerIdentity",
            "SetNewSignerIdentity",
            "sso.version.version1",
            (
                ("signingKey", "string", "sso.version.version1", F_SECRET, None),
                (
                    "signingCertificateChain",
                    "sso.admin.ConfigurationManagementService.CertificateChain",
                    "sso.version.version1",
                    0,
                    None,
                ),
            ),
            (0, "void", "void"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "setSignerIdentity",
            "SetSignerIdentity",
            "sso.version.version1",
            (
                ("adminUser", "sso.PrincipalId", "sso.version.version1", 0, None),
                ("adminPass", "string", "sso.version.version1", F_SECRET, None),
                ("signingKey", "string", "sso.version.version1", F_SECRET, None),
                (
                    "signingCertificateChain",
                    "sso.admin.ConfigurationManagementService.CertificateChain",
                    "sso.version.version1",
                    0,
                    None,
                ),
            ),
            (0, "void", "void"),
            None,
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "getClockTolerance",
            "GetClockTolerance",
            "sso.version.version1",
            (),
            (0, "long", "long"),
            "System.Anonymous",
            [
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "setClockTolerance",
            "SetClockTolerance",
            "sso.version.version1",
            (("milliseconds", "long", "sso.version.version1", 0, None),),
            (0, "void", "void"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "getDelegationCount",
            "GetDelegationCount",
            "sso.version.version1",
            (),
            (0, "int", "int"),
            "System.Read",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "setDelegationCount",
            "SetDelegationCount",
            "sso.version.version1",
            (("delegationCount", "int", "sso.version.version1", 0, None),),
            (0, "void", "void"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "getRenewCount",
            "GetRenewCount",
            "sso.version.version1",
            (),
            (0, "int", "int"),
            "System.Read",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "setRenewCount",
            "SetRenewCount",
            "sso.version.version1",
            (("renewCount", "int", "sso.version.version1", 0, None),),
            (0, "void", "void"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "getMaximumBearerTokenLifetime",
            "GetMaximumBearerTokenLifetime",
            "sso.version.version1",
            (),
            (0, "long", "long"),
            "System.Read",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "setMaximumBearerTokenLifetime",
            "SetMaximumBearerTokenLifetime",
            "sso.version.version1",
            (("maxLifetime", "long", "sso.version.version1", 0, None),),
            (0, "void", "void"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "getMaximumHoKTokenLifetime",
            "GetMaximumHoKTokenLifetime",
            "sso.version.version1",
            (),
            (0, "long", "long"),
            "System.Read",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "setMaximumHoKTokenLifetime",
            "SetMaximumHoKTokenLifetime",
            "sso.version.version1",
            (("maxLifetime", "long", "sso.version.version1", 0, None),),
            (0, "void", "void"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "getPasswordExpirationConfiguration",
            "GetPasswordExpirationConfiguration",
            "sso.version.version1",
            (),
            (
                0,
                "sso.admin.PasswordExpirationConfig",
                "sso.admin.PasswordExpirationConfig",
            ),
            "System.Read",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "updatePasswordExpirationConfiguration",
            "UpdatePasswordExpirationConfiguration",
            "sso.version.version1",
            (
                (
                    "config",
                    "sso.admin.PasswordExpirationConfig",
                    "sso.version.version1",
                    0,
                    None,
                ),
            ),
            (0, "void", "void"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "importSAMLMetadata",
            "ImportSAMLMetadata",
            "sso.version.version2",
            (("samlConfigDoc", "string", "sso.version.version2", 0, None),),
            (0, "void", "void"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "deleteRelyingParty",
            "DeleteRelyingParty",
            "sso.version.version2",
            (("rpName", "string", "sso.version.version2", 0, None),),
            (0, "void", "void"),
            "Sso.AdminServer.Administer",
            [
                "sso.admin.fault.NoSuchRelyingPartyFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "getIssuerName",
            "GetIssuerName",
            "sso.version.version1_5",
            (),
            (0, "string", "string"),
            "System.Anonymous",
            None,
        ),
        (
            "isExternalIDPJitEnabled",
            "IsExternalIDPJitEnabled",
            "sso.version.version3_5",
            (("entityID", "string", "sso.version.version3_5", 0, None),),
            (0, "boolean", "boolean"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.NotAuthenticated",
                "sso.admin.fault.NoSuchConfigFault",
            ],
        ),
        (
            "setExternalIDPJitAttribute",
            "SetExternalIDPJitAttribute",
            "sso.version.version3_5",
            (
                ("entityID", "string", "sso.version.version3_5", 0, None),
                ("enableJit", "boolean", "sso.version.version3_5", 0, None),
            ),
            (0, "void", "void"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
            ],
        ),
        (
            "setAuthnPolicy",
            "SetAuthnPolicy",
            "sso.version.version3_2",
            (("policy", "sso.admin.AuthnPolicy", "sso.version.version3_2", 0, None),),
            (0, "void", "void"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
            ],
        ),
        (
            "getAuthnPolicy",
            "GetAuthnPolicy",
            "sso.version.version3_2",
            (),
            (F_OPTIONAL, "sso.admin.AuthnPolicy", "sso.admin.AuthnPolicy"),
            "System.Read",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
            ],
        ),
    ],
)
CreateDataType(
    "sso.admin.ConfigurationManagementService.CertificateChain",
    "SsoAdminConfigurationManagementServiceCertificateChain",
    "vmodl.DynamicData",
    "sso.version.version1",
    [("certificates", "string[]", "sso.version.version1", 0)],
)
CreateDataType(
    "sso.admin.ConfigurationManagementService.AttributeConfig",
    "SsoAdminConfigurationManagementServiceAttributeConfig",
    "vmodl.DynamicData",
    "sso.version.version2",
    [
        ("tokenAttribute", "string", "sso.version.version2", 0),
        ("storeAttribute", "string", "sso.version.version2", 0),
    ],
)
CreateDataType(
    "sso.admin.ConfigurationManagementService.TokenClaimAttribute",
    "SsoAdminConfigurationManagementServiceTokenClaimAttribute",
    "vmodl.DynamicData",
    "sso.version.version3_5",
    [
        ("claimName", "string", "sso.version.version3_5", 0),
        ("claimValue", "string", "sso.version.version3_5", 0),
    ],
)
CreateDataType(
    "sso.admin.ConfigurationManagementService.TokenClaimGroupMapping",
    "SsoAdminConfigurationManagementServiceTokenClaimGroupMapping",
    "vmodl.DynamicData",
    "sso.version.version3_5",
    [
        (
            "tokenClaim",
            "sso.admin.ConfigurationManagementService.TokenClaimAttribute",
            "sso.version.version3_5",
            0,
        ),
        ("groups", "string[]", "sso.version.version3_5", 0),
    ],
)
CreateManagedType(
    "sso.admin.DeploymentInformationService",
    "SsoAdminDeploymentInformationService",
    "vmodl.ManagedObject",
    "sso.version.version1",
    None,
    [
        (
            "isMultiSiteDeployment",
            "IsMultiSiteDeployment",
            "sso.version.version1",
            (),
            (0, "boolean", "boolean"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
                "sso.fault.InternalFault",
            ],
        ),
        (
            "retrieveHaBackupConfigurationPackage",
            "RetrieveHaBackupConfigurationPackage",
            "sso.version.version1",
            (),
            (0, "vmodl.Binary", "vmodl.Binary"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
                "sso.fault.InternalFault",
            ],
        ),
        (
            "retrieveReplicaConfigurationPackage",
            "RetrieveReplicaConfigurationPackage",
            "sso.version.version1",
            (),
            (0, "vmodl.Binary", "vmodl.Binary"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
                "sso.fault.InternalFault",
                "vmodl.fault.NotSupported",
            ],
        ),
    ],
)
CreateDataType(
    "sso.admin.Domain",
    "SsoAdminDomain",
    "vmodl.DynamicData",
    "sso.version.version1_5",
    [
        ("name", "string", "sso.version.version1_5", 0),
        ("alias", "string", "sso.version.version1_5", F_OPTIONAL),
    ],
)
CreateManagedType(
    "sso.admin.DomainManagementService",
    "SsoAdminDomainManagementService",
    "vmodl.ManagedObject",
    "sso.version.version1",
    None,
    [
        (
            "probeConnectivity",
            "ProbeConnectivity",
            "sso.version.version1",
            (
                ("serviceUri", "vmodl.URI", "sso.version.version1", 0, None),
                ("authenticationType", "string", "sso.version.version1", 0, None),
                (
                    "authnCredentials",
                    "sso.admin.DomainManagementService.AuthenticationCredentails",
                    "sso.version.version1",
                    F_OPTIONAL,
                    None,
                ),
                (
                    "certificates",
                    "string[]",
                    "sso.version.version3_5",
                    F_OPTIONAL,
                    None,
                ),
            ),
            (0, "void", "void"),
            "Sso.AdminServer.Administer",
            [
                "sso.admin.fault.DirectoryServiceConnectionFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "addExternalDomain",
            "AddExternalDomain",
            "sso.version.version1",
            (
                ("serverType", "string", "sso.version.version1", 0, None),
                ("domainName", "string", "sso.version.version1", 0, None),
                ("domainAlias", "string", "sso.version.version1", F_OPTIONAL, None),
                (
                    "details",
                    "sso.admin.ExternalDomainDetails",
                    "sso.version.version1",
                    0,
                    None,
                ),
                ("authenticationType", "string", "sso.version.version1", 0, None),
                (
                    "authnCredentials",
                    "sso.admin.DomainManagementService.AuthenticationCredentails",
                    "sso.version.version1",
                    F_OPTIONAL,
                    None,
                ),
            ),
            (0, "void", "void"),
            "Sso.AdminServer.Administer",
            [
                "sso.admin.fault.DirectoryServiceConnectionFault",
                "sso.admin.fault.DuplicateDomainNameFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "registerLocalOSDomain",
            "RegisterLocalOSDomain",
            "sso.version.version1",
            (("domainName", "string", "sso.version.version1", 0, None),),
            (0, "void", "void"),
            "Sso.AdminServer.Administer",
            [
                "sso.admin.fault.DuplicateDomainNameFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
                "sso.admin.fault.LocalOSDomainRegistrationFault",
            ],
        ),
        (
            "getDomains",
            "GetDomains",
            "sso.version.version1",
            (),
            (0, "sso.admin.Domains", "sso.admin.Domains"),
            "System.Read",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "findExternalDomain",
            "FindExternalDomain",
            "sso.version.version1",
            (("name", "string", "sso.version.version1", 0, None),),
            (F_OPTIONAL, "sso.admin.ExternalDomain", "sso.admin.ExternalDomain"),
            "System.Read",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "setBrandName",
            "SetBrandName",
            "sso.version.version2",
            (("brandName", "string", "sso.version.version2", F_OPTIONAL, None),),
            (0, "void", "void"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "getBrandName",
            "GetBrandName",
            "sso.version.version2",
            (),
            (F_OPTIONAL, "string", "string"),
            "System.Read",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "setLogonBanner",
            "SetLogonBanner",
            "sso.version.version3_1",
            (("logonBanner", "string", "sso.version.version3_1", F_OPTIONAL, None),),
            (0, "void", "void"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "getLogonBanner",
            "GetLogonBanner",
            "sso.version.version3_1",
            (),
            (F_OPTIONAL, "string", "string"),
            "System.Read",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "setLogonBannerTitle",
            "SetLogonBannerTitle",
            "sso.version.version3_2",
            (
                (
                    "logonBannerTitle",
                    "string",
                    "sso.version.version3_2",
                    F_OPTIONAL,
                    None,
                ),
            ),
            (0, "void", "void"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "getLogonBannerTitle",
            "GetLogonBannerTitle",
            "sso.version.version3_2",
            (),
            (F_OPTIONAL, "string", "string"),
            "System.Read",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "setLogonBannerContent",
            "SetLogonBannerContent",
            "sso.version.version3_2",
            (
                (
                    "logonBannerContent",
                    "string",
                    "sso.version.version3_2",
                    F_OPTIONAL,
                    None,
                ),
            ),
            (0, "void", "void"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "getLogonBannerContent",
            "GetLogonBannerContent",
            "sso.version.version3_2",
            (),
            (F_OPTIONAL, "string", "string"),
            "System.Read",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "setLogonBannerCheckboxFlag",
            "SetLogonBannerCheckboxFlag",
            "sso.version.version3_2",
            (
                (
                    "enableLogonBannerCheckbox",
                    "boolean",
                    "sso.version.version3_2",
                    F_OPTIONAL,
                    None,
                ),
            ),
            (0, "void", "void"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "getLogonBannerCheckboxFlag",
            "GetLogonBannerCheckboxFlag",
            "sso.version.version3_2",
            (),
            (F_OPTIONAL, "boolean", "boolean"),
            "System.Read",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "disableLogonBanner",
            "DisableLogonBanner",
            "sso.version.version3_2",
            (),
            (0, "void", "void"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "isLogonBannerDisabled",
            "IsLogonBannerDisabled",
            "sso.version.version3_2",
            (),
            (F_OPTIONAL, "boolean", "boolean"),
            "System.Read",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "getSystemDomainName",
            "GetSystemDomainName",
            "sso.version.version1",
            (),
            (0, "string", "string"),
            "System.Anonymous",
            [
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "getSystemTenantName",
            "GetSystemTenantName",
            "sso.version.version2",
            (),
            (0, "string", "string"),
            "System.Anonymous",
            [
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "getLocalOSDomainName",
            "GetLocalOSDomainName",
            "sso.version.version1",
            (),
            (F_OPTIONAL, "string", "string"),
            "System.Read",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "updateExternalDomainDetails",
            "UpdateExternalDomainDetails",
            "sso.version.version1",
            (
                ("name", "string", "sso.version.version1", 0, None),
                (
                    "details",
                    "sso.admin.ExternalDomainDetails",
                    "sso.version.version1",
                    0,
                    None,
                ),
            ),
            (0, "void", "void"),
            "Sso.AdminServer.Administer",
            [
                "sso.admin.fault.DomainNotFoundFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "updateExternalDomainAuthnType",
            "UpdateExternalDomainAuthnType",
            "sso.version.version1",
            (
                ("name", "string", "sso.version.version1", 0, None),
                ("authnType", "string", "sso.version.version1", 0, None),
                (
                    "authnCredentials",
                    "sso.admin.DomainManagementService.AuthenticationCredentails",
                    "sso.version.version1",
                    F_OPTIONAL,
                    None,
                ),
            ),
            (0, "void", "void"),
            "Sso.AdminServer.Administer",
            [
                "sso.admin.fault.DomainNotFoundFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "registerUpnSuffix",
            "RegisterUpnSuffix",
            "sso.version.version2_5",
            (
                ("domainName", "string", "sso.version.version2_5", 0, None),
                ("upnSuffix", "string", "sso.version.version2_5", 0, None),
            ),
            (0, "boolean", "boolean"),
            "Sso.AdminServer.Administer",
            [
                "sso.admin.fault.DomainNotFoundFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "unRegisterUpnSuffix",
            "UnRegisterUpnSuffix",
            "sso.version.version2_5",
            (
                ("domainName", "string", "sso.version.version2_5", 0, None),
                ("upnSuffix", "string", "sso.version.version2_5", 0, None),
            ),
            (0, "boolean", "boolean"),
            "Sso.AdminServer.Administer",
            [
                "sso.admin.fault.DomainNotFoundFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "getUpnSuffixes",
            "GetUpnSuffixes",
            "sso.version.version2_5",
            (("domainName", "string", "sso.version.version2_5", 0, None),),
            (F_OPTIONAL, "string[]", "string[]"),
            "System.Read",
            [
                "sso.admin.fault.DomainNotFoundFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "deleteDomain",
            "DeleteDomain",
            "sso.version.version1",
            (("name", "string", "sso.version.version1", 0, None),),
            (0, "void", "void"),
            "Sso.AdminServer.Administer",
            [
                "sso.admin.fault.DomainNotFoundFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "getSslCertificateManager",
            "GetSslCertificateManager",
            "sso.version.version1",
            (),
            (0, "sso.admin.CertificateManager", "sso.admin.CertificateManager"),
            "System.Anonymous",
            [
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "setDefaultDomains",
            "SetDefaultDomains",
            "sso.version.version1",
            (("domainNames", "string[]", "sso.version.version1", F_OPTIONAL, None),),
            (0, "void", "void"),
            "Sso.AdminServer.Administer",
            [
                "sso.admin.fault.DomainNotFoundFault",
                "sso.admin.fault.DuplicateDomainNameFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "getDefaultDomains",
            "GetDefaultDomains",
            "sso.version.version1",
            (),
            (F_OPTIONAL, "string[]", "string[]"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "getSslIdentity",
            "GetSslIdentity",
            "sso.version.version1_5",
            (
                ("host", "string", "sso.version.version1_5", 0, None),
                ("ldapsPort", "int", "sso.version.version1_5", 0, None),
            ),
            (
                F_OPTIONAL,
                "sso.admin.ConfigurationManagementService.CertificateChain",
                "sso.admin.ConfigurationManagementService.CertificateChain",
            ),
            "System.Read",
            [
                "sso.admin.fault.DirectoryServiceConnectionFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
    ],
)
CreateDataType(
    "sso.admin.DomainManagementService.AuthenticationCredentails",
    "SsoAdminDomainManagementServiceAuthenticationCredentails",
    "vmodl.DynamicData",
    "sso.version.version1",
    [
        ("username", "string", "sso.version.version1", 0),
        ("password", "string", "sso.version.version1", F_SECRET),
        ("useMachineAccount", "boolean", "sso.version.version1_5", F_OPTIONAL),
        ("spn", "string", "sso.version.version1_5", F_OPTIONAL),
    ],
)
CreateDataType(
    "sso.admin.Domains",
    "SsoAdminDomains",
    "vmodl.DynamicData",
    "sso.version.version1",
    [
        (
            "externalDomains",
            "sso.admin.ExternalDomain[]",
            "sso.version.version1",
            F_OPTIONAL,
        ),
        ("systemDomainName", "string", "sso.version.version1", 0),
        ("systemDomainUpnSuffixes", "string[]", "sso.version.version2_5", F_OPTIONAL),
        ("localOSDomainName", "string", "sso.version.version1", F_OPTIONAL),
    ],
)
CreateDataType(
    "sso.admin.ExternalDomain",
    "SsoAdminExternalDomain",
    "vmodl.DynamicData",
    "sso.version.version1",
    [
        ("type", "string", "sso.version.version1", 0),
        ("name", "string", "sso.version.version1", 0),
        ("alias", "string", "sso.version.version1", F_OPTIONAL),
        ("details", "sso.admin.ExternalDomainDetails", "sso.version.version1", 0),
        (
            "authenticationDetails",
            "sso.admin.ExternalDomain.AuthenticationDetails",
            "sso.version.version1",
            0,
        ),
    ],
)
CreateEnumType(
    "sso.admin.ExternalDomain.Type",
    "SsoAdminExternalDomainType",
    "sso.version.version1",
    ["ActiveDirectory", "OpenLdap", "NIS"],
)
CreateEnumType(
    "sso.admin.ExternalDomain.AuthenticationType",
    "SsoAdminExternalDomainAuthenticationType",
    "sso.version.version1",
    ["anonymous", "password", "reuseSession"],
)
CreateDataType(
    "sso.admin.ExternalDomain.AuthenticationDetails",
    "SsoAdminExternalDomainAuthenticationDetails",
    "vmodl.DynamicData",
    "sso.version.version1",
    [
        ("authenticationType", "string", "sso.version.version1", 0),
        ("username", "string", "sso.version.version1", F_OPTIONAL),
    ],
)
CreateDataType(
    "sso.admin.ExternalDomainAttributeMapping",
    "SsoAdminExternalDomainAttributeMapping",
    "vmodl.DynamicData",
    "sso.version.version1_5",
    [
        ("attributeId", "string", "sso.version.version1_5", 0),
        ("attributeName", "string", "sso.version.version1_5", 0),
    ],
)
CreateEnumType(
    "sso.admin.ExternalDomainAttributeMapping.AttributeIds",
    "SsoAdminExternalDomainAttributeMappingAttributeIds",
    "sso.version.version1_5",
    [
        "UserAttributeAccountName",
        "UserAttributeLastName",
        "UserAttributeFirstName",
        "UserAttributeDescription",
        "UserAttributeDisplayName",
        "UserAttributeEmail",
        "UserAttributeObjectId",
        "UserAttributePrincipalName",
        "UserAttributeAcountControl",
        "UserAttributeMemberOf",
        "UserAttributePrimaryGroupId",
        "UserAttributeLockoutTime",
        "UserAttributePasswordSettingsObject",
        "UserAttributePwdLastSet",
        "GroupAttributeAccountName",
        "GroupAttributeDescription",
        "GroupAttributeObjectId",
        "GroupAttributeMemberOf",
        "GroupAttributeMembersList",
        "PasswordSettingsAttributeMaximumPwdAge",
        "DomainAttributeMaxPwdAge",
    ],
)
CreateDataType(
    "sso.admin.ExternalDomainDetails",
    "SsoAdminExternalDomainDetails",
    "vmodl.DynamicData",
    "sso.version.version1",
    [
        ("friendlyName", "string", "sso.version.version1", 0),
        ("userBaseDn", "string", "sso.version.version1", F_OPTIONAL),
        ("groupBaseDn", "string", "sso.version.version1", F_OPTIONAL),
        ("primaryUrl", "vmodl.URI", "sso.version.version1", 0),
        ("failoverUrl", "vmodl.URI", "sso.version.version1", F_OPTIONAL),
        ("searchTimeoutSeconds", "int", "sso.version.version1", 0),
        (
            "schemaDetails",
            "sso.admin.ExternalDomainSchemaDetails",
            "sso.version.version2",
            F_OPTIONAL,
        ),
        ("upnSuffixes", "string[]", "sso.version.version2_5", F_OPTIONAL),
    ],
)
CreateDataType(
    "sso.admin.ExternalDomainObjectMapping",
    "SsoAdminExternalDomainObjectMapping",
    "vmodl.DynamicData",
    "sso.version.version1_5",
    [
        ("objectId", "string", "sso.version.version1_5", 0),
        ("objectClass", "string", "sso.version.version1_5", F_OPTIONAL),
        (
            "attributeMappings",
            "sso.admin.ExternalDomainAttributeMapping[]",
            "sso.version.version1_5",
            F_OPTIONAL,
        ),
    ],
)
CreateEnumType(
    "sso.admin.ExternalDomainObjectMapping.ObjectIds",
    "SsoAdminExternalDomainObjectMappingObjectIds",
    "sso.version.version1_5",
    ["ObjectIdUser", "ObjectIdGroup", "ObjectIdPasswordSettings", "ObjectIdDomain"],
)
CreateDataType(
    "sso.admin.ExternalDomainSchemaDetails",
    "SsoAdminExternalDomainSchemaDetails",
    "vmodl.DynamicData",
    "sso.version.version1_5",
    [
        (
            "objectMappings",
            "sso.admin.ExternalDomainObjectMapping[]",
            "sso.version.version1_5",
            F_OPTIONAL,
        )
    ],
)
CreateDataType(
    "sso.admin.Group",
    "SsoAdminGroup",
    "vmodl.DynamicData",
    "sso.version.version1",
    [
        ("id", "sso.PrincipalId", "sso.version.version1", 0),
        ("alias", "sso.PrincipalId", "sso.version.version1", F_OPTIONAL),
        ("details", "sso.admin.GroupDetails", "sso.version.version1", 0),
    ],
)
CreateDataType(
    "sso.admin.GroupDetails",
    "SsoAdminGroupDetails",
    "vmodl.DynamicData",
    "sso.version.version1",
    [("description", "string", "sso.version.version1", F_OPTIONAL)],
)
CreateDataType(
    "sso.admin.IDPConfiguration",
    "SsoAdminIDPConfiguration",
    "vmodl.DynamicData",
    "sso.version.version3",
    [
        ("entityID", "string", "sso.version.version3", 0),
        ("nameIDFormats", "string[]", "sso.version.version3", F_OPTIONAL),
        (
            "ssoServices",
            "sso.admin.ServiceEndpoint[]",
            "sso.version.version3",
            F_OPTIONAL,
        ),
        (
            "sloServices",
            "sso.admin.ServiceEndpoint[]",
            "sso.version.version3",
            F_OPTIONAL,
        ),
        ("signingCertificateChain", "string[]", "sso.version.version3", 0),
        (
            "subjectFormatMappings",
            "sso.admin.ConfigurationManagementService.AttributeConfig[]",
            "sso.version.version3",
            F_OPTIONAL,
        ),
        ("isJitEnabled", "boolean", "sso.version.version3_5", F_OPTIONAL),
        (
            "tokenClaimGroupMappings",
            "sso.admin.ConfigurationManagementService.TokenClaimGroupMapping[]",
            "sso.version.version3_5",
            F_OPTIONAL,
        ),
        ("upnSuffix", "string", "sso.version.version3_5", F_OPTIONAL),
    ],
)
CreateDataType(
    "sso.admin.IdentitySource",
    "SsoAdminIdentitySource",
    "vmodl.DynamicData",
    "sso.version.version1_5",
    [
        ("name", "string", "sso.version.version1_5", 0),
        ("domains", "sso.admin.Domain[]", "sso.version.version1_5", 0),
    ],
)
CreateManagedType(
    "sso.admin.IdentitySourceManagementService",
    "SsoAdminIdentitySourceManagementService",
    "vmodl.ManagedObject",
    "sso.version.version1_5",
    None,
    [
        (
            "registerLdap",
            "RegisterLdap",
            "sso.version.version1_5",
            (
                ("serverType", "string", "sso.version.version1_5", 0, None),
                ("domainName", "string", "sso.version.version1_5", 0, None),
                ("domainAlias", "string", "sso.version.version1_5", F_OPTIONAL, None),
                (
                    "details",
                    "sso.admin.LdapIdentitySourceDetails",
                    "sso.version.version1_5",
                    0,
                    None,
                ),
                ("authenticationType", "string", "sso.version.version1_5", 0, None),
                (
                    "authnCredentials",
                    "sso.admin.IdentitySourceManagementService.AuthenticationCredentials",
                    "sso.version.version1_5",
                    F_OPTIONAL,
                    None,
                ),
            ),
            (0, "void", "void"),
            "Sso.IdentitySource.Administer",
            [
                "sso.admin.fault.DuplicateDomainNameFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
                "sso.admin.fault.DirectoryServiceConnectionFault",
                "sso.admin.fault.ADIDSAlreadyExistFault",
                "sso.admin.fault.InvalidProviderFault",
            ],
        ),
        (
            "registerActiveDirectory",
            "RegisterActiveDirectory",
            "sso.version.version1_5",
            (
                ("domainName", "string", "sso.version.version1_5", 0, None),
                (
                    "authnCredentials",
                    "sso.admin.IdentitySourceManagementService.AuthenticationCredentials",
                    "sso.version.version1_5",
                    0,
                    None,
                ),
                (
                    "schemaMapping",
                    "sso.admin.ExternalDomainSchemaDetails",
                    "sso.version.version1_5",
                    F_OPTIONAL,
                    None,
                ),
            ),
            (0, "void", "void"),
            "Sso.IdentitySource.Administer",
            [
                "sso.admin.fault.DuplicateDomainNameFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
                "sso.admin.fault.ADIDSAlreadyExistFault",
                "sso.admin.fault.HostNotJoinedRequiredDomainFault",
                "sso.admin.fault.DomainManagerFault",
                "sso.fault.InvalidPrincipalFault",
            ],
        ),
        (
            "registerLocalOS",
            "RegisterLocalOS",
            "sso.version.version1_5",
            (("name", "string", "sso.version.version1_5", 0, None),),
            (0, "void", "void"),
            "Sso.IdentitySource.Administer",
            [
                "sso.admin.fault.DuplicateDomainNameFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
                "sso.admin.fault.LocalOSDomainRegistrationFault",
            ],
        ),
        (
            "get",
            "Get",
            "sso.version.version1_5",
            (),
            (0, "sso.admin.IdentitySources", "sso.admin.IdentitySources"),
            "System.Read",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "getActiveDirectoryAuthnAccountInfo",
            "GetActiveDirectoryAuthnAccountInfo",
            "sso.version.version1_5",
            (),
            (
                F_OPTIONAL,
                "sso.admin.AuthenticationAccountInfo",
                "sso.admin.AuthenticationAccountInfo",
            ),
            "System.Read",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "getSystemDomainName",
            "IdS_getSystemDomainName",
            "sso.version.version1_5",
            (),
            (0, "string", "string"),
            "System.Anonymous",
            [
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "updateLdap",
            "UpdateLdap",
            "sso.version.version1_5",
            (
                ("name", "string", "sso.version.version1_5", 0, None),
                (
                    "details",
                    "sso.admin.LdapIdentitySourceDetails",
                    "sso.version.version1_5",
                    0,
                    None,
                ),
            ),
            (0, "void", "void"),
            "Sso.IdentitySource.Administer",
            [
                "sso.admin.fault.DomainNotFoundFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
                "sso.admin.fault.DirectoryServiceConnectionFault",
                "sso.admin.fault.InvalidProviderFault",
            ],
        ),
        (
            "updateActiveDirectory",
            "UpdateActiveDirectory",
            "sso.version.version1_5",
            (
                ("domainName", "string", "sso.version.version1_5", 0, None),
                (
                    "authnCredentials",
                    "sso.admin.IdentitySourceManagementService.AuthenticationCredentials",
                    "sso.version.version1_5",
                    0,
                    None,
                ),
                (
                    "schemaMapping",
                    "sso.admin.ExternalDomainSchemaDetails",
                    "sso.version.version1_5",
                    F_OPTIONAL,
                    None,
                ),
            ),
            (0, "void", "void"),
            "Sso.IdentitySource.Administer",
            [
                "sso.admin.fault.DomainNotFoundFault",
                "sso.admin.fault.DomainManagerFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
                "sso.fault.InvalidPrincipalFault",
                "sso.admin.fault.DuplicateDomainNameFault",
            ],
        ),
        (
            "updateLdapAuthnType",
            "UpdateLdapAuthnType",
            "sso.version.version1_5",
            (
                ("name", "string", "sso.version.version1_5", 0, None),
                ("authnType", "string", "sso.version.version1_5", 0, None),
                (
                    "authnCredentials",
                    "sso.admin.IdentitySourceManagementService.AuthenticationCredentials",
                    "sso.version.version1_5",
                    F_OPTIONAL,
                    None,
                ),
            ),
            (0, "void", "void"),
            "Sso.IdentitySource.Administer",
            [
                "sso.admin.fault.DomainNotFoundFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
                "sso.admin.fault.DirectoryServiceConnectionFault",
            ],
        ),
        (
            "delete",
            "Delete",
            "sso.version.version1_5",
            (("name", "string", "sso.version.version1_5", 0, None),),
            (0, "void", "void"),
            "Sso.IdentitySource.Administer",
            [
                "sso.admin.fault.DomainNotFoundFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "setDefaultDomains",
            "IdS_setDefaultDomains",
            "sso.version.version1_5",
            (("domainNames", "string[]", "sso.version.version1_5", F_OPTIONAL, None),),
            (0, "void", "void"),
            "Sso.IdentitySource.Administer",
            [
                "sso.admin.fault.DomainNotFoundFault",
                "sso.admin.fault.DuplicateDomainNameFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "getDefaultDomains",
            "IdS_getDefaultDomains",
            "sso.version.version1_5",
            (),
            (F_OPTIONAL, "string[]", "string[]"),
            "Sso.IdentitySource.Administer",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "getSslCertificateManager",
            "IdS_getSslCertificateManager",
            "sso.version.version1_5",
            (),
            (0, "sso.admin.CertificateManager", "sso.admin.CertificateManager"),
            "System.Anonymous",
            [
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "probeConnectivity",
            "IdS_probeConnectivity",
            "sso.version.version1_5",
            (
                ("serviceUri", "vmodl.URI", "sso.version.version1_5", 0, None),
                ("authenticationType", "string", "sso.version.version1_5", 0, None),
                (
                    "authnCredentials",
                    "sso.admin.IdentitySourceManagementService.AuthenticationCredentials",
                    "sso.version.version1_5",
                    F_OPTIONAL,
                    None,
                ),
                (
                    "certificates",
                    "string[]",
                    "sso.version.version3_5",
                    F_OPTIONAL,
                    None,
                ),
            ),
            (0, "void", "void"),
            "Sso.IdentitySource.Administer",
            [
                "sso.admin.fault.DirectoryServiceConnectionFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "probeLdapConnectivity",
            "IdS_probeLdapConnectivity",
            "sso.version.version3_5",
            (
                ("domainName", "string", "sso.version.version3_5", 0, None),
                (
                    "authnCredential",
                    "sso.admin.IdentitySourceManagementService.AuthenticationCredentials",
                    "sso.version.version3_5",
                    0,
                    None,
                ),
                (
                    "identitySource",
                    "sso.admin.LdapIdentitySource",
                    "sso.version.version3_5",
                    0,
                    None,
                ),
            ),
            (0, "void", "void"),
            "Sso.IdentitySource.Administer",
            [
                "sso.admin.fault.DirectoryServiceConnectionFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "getSslIdentity",
            "IdS_getSslIdentity",
            "sso.version.version1_5",
            (
                ("host", "string", "sso.version.version1_5", 0, None),
                ("ldapsPort", "int", "sso.version.version1_5", 0, None),
            ),
            (
                F_OPTIONAL,
                "sso.admin.ConfigurationManagementService.CertificateChain",
                "sso.admin.ConfigurationManagementService.CertificateChain",
            ),
            "System.Read",
            [
                "sso.admin.fault.DirectoryServiceConnectionFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
    ],
)
CreateDataType(
    "sso.admin.IdentitySourceManagementService.AuthenticationCredentials",
    "SsoAdminIdentitySourceManagementServiceAuthenticationCredentials",
    "vmodl.DynamicData",
    "sso.version.version1_5",
    [
        ("username", "string", "sso.version.version1_5", 0),
        ("password", "string", "sso.version.version1_5", F_SECRET),
        ("useMachineAccount", "boolean", "sso.version.version1_5", F_OPTIONAL),
        ("spn", "string", "sso.version.version1_5", F_OPTIONAL),
    ],
)
CreateDataType(
    "sso.admin.IdentitySources",
    "SsoAdminIdentitySources",
    "vmodl.DynamicData",
    "sso.version.version1_5",
    [
        ("all", "sso.admin.IdentitySource[]", "sso.version.version1_5", 0),
        ("system", "sso.admin.IdentitySource", "sso.version.version1_5", 0),
        ("localOS", "sso.admin.IdentitySource", "sso.version.version1_5", F_OPTIONAL),
        (
            "ldaps",
            "sso.admin.LdapIdentitySource[]",
            "sso.version.version1_5",
            F_OPTIONAL,
        ),
        ("nativeAD", "sso.admin.IdentitySource", "sso.version.version1_5", F_OPTIONAL),
    ],
)
CreateDataType(
    "sso.admin.LdapIdentitySource",
    "SsoAdminLdapIdentitySource",
    "sso.admin.IdentitySource",
    "sso.version.version1_5",
    [
        ("type", "string", "sso.version.version1_5", 0),
        ("details", "sso.admin.LdapIdentitySourceDetails", "sso.version.version1_5", 0),
        (
            "authenticationDetails",
            "sso.admin.LdapIdentitySource.AuthenticationDetails",
            "sso.version.version1_5",
            0,
        ),
    ],
)
CreateEnumType(
    "sso.admin.LdapIdentitySource.Type",
    "SsoAdminLdapIdentitySourceType",
    "sso.version.version1_5",
    ["ActiveDirectory", "OpenLdap"],
)
CreateEnumType(
    "sso.admin.LdapIdentitySource.AuthenticationType",
    "SsoAdminLdapIdentitySourceAuthenticationType",
    "sso.version.version1_5",
    ["anonymous", "password", "reuseSession"],
)
CreateDataType(
    "sso.admin.LdapIdentitySource.AuthenticationDetails",
    "SsoAdminLdapIdentitySourceAuthenticationDetails",
    "vmodl.DynamicData",
    "sso.version.version1_5",
    [
        ("authenticationType", "string", "sso.version.version1_5", 0),
        ("username", "string", "sso.version.version1_5", F_OPTIONAL),
    ],
)
CreateDataType(
    "sso.admin.LdapIdentitySourceDetails",
    "SsoAdminLdapIdentitySourceDetails",
    "vmodl.DynamicData",
    "sso.version.version1_5",
    [
        ("friendlyName", "string", "sso.version.version1_5", 0),
        ("userBaseDn", "string", "sso.version.version1_5", F_OPTIONAL),
        ("groupBaseDn", "string", "sso.version.version1_5", F_OPTIONAL),
        ("primaryUrl", "vmodl.URI", "sso.version.version1_5", 0),
        ("failoverUrl", "vmodl.URI", "sso.version.version1_5", F_OPTIONAL),
        ("searchTimeoutSeconds", "int", "sso.version.version1_5", 0),
        ("isSiteAffinityEnabled", "boolean", "sso.version.version3_5", F_OPTIONAL),
        ("certificates", "string[]", "sso.version.version3_5", F_OPTIONAL),
    ],
)
CreateDataType(
    "sso.admin.LockoutPolicy",
    "SsoAdminLockoutPolicy",
    "vmodl.DynamicData",
    "sso.version.version1",
    [
        ("description", "string", "sso.version.version1", F_OPTIONAL),
        ("maxFailedAttempts", "int", "sso.version.version1", 0),
        ("failedAttempts", "int", "sso.version.version2", 0),
        ("failedAttemptIntervalSec", "long", "sso.version.version1", 0),
        ("autoUnlockIntervalSec", "long", "sso.version.version1", 0),
    ],
)
CreateManagedType(
    "sso.admin.LockoutPolicyService",
    "SsoAdminLockoutPolicyService",
    "vmodl.ManagedObject",
    "sso.version.version1",
    None,
    [
        (
            "getLockoutPolicy",
            "GetLockoutPolicy",
            "sso.version.version1",
            (),
            (0, "sso.admin.LockoutPolicy", "sso.admin.LockoutPolicy"),
            "System.Read",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "updateLockoutPolicy",
            "UpdateLockoutPolicy",
            "sso.version.version1",
            (("policy", "sso.admin.LockoutPolicy", "sso.version.version1", 0, None),),
            (0, "void", "void"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
    ],
)
CreateDataType(
    "sso.admin.MailContent",
    "SsoAdminMailContent",
    "vmodl.DynamicData",
    "sso.version.version1",
    [
        ("from", "string", "sso.version.version1", 0),
        ("to", "string", "sso.version.version1", 0),
        ("subject", "string", "sso.version.version1", 0),
        ("content", "string", "sso.version.version1", 0),
    ],
)
CreateDataType(
    "sso.admin.PasswordExpirationConfig",
    "SsoAdminPasswordExpirationConfig",
    "vmodl.DynamicData",
    "sso.version.version1",
    [
        ("emailNotificationEnabled", "boolean", "sso.version.version1", 0),
        ("emailFrom", "string", "sso.version.version1", F_OPTIONAL),
        ("emailSubject", "string", "sso.version.version1", F_OPTIONAL),
        ("notificationDays", "int[]", "sso.version.version1", F_OPTIONAL),
    ],
)
CreateDataType(
    "sso.admin.PasswordFormat",
    "SsoAdminPasswordFormat",
    "vmodl.DynamicData",
    "sso.version.version1",
    [
        (
            "lengthRestriction",
            "sso.admin.PasswordFormat.LengthRestriction",
            "sso.version.version1",
            0,
        ),
        (
            "alphabeticRestriction",
            "sso.admin.PasswordFormat.AlphabeticRestriction",
            "sso.version.version1",
            0,
        ),
        ("minNumericCount", "int", "sso.version.version1", 0),
        ("minSpecialCharCount", "int", "sso.version.version1", 0),
        ("maxIdenticalAdjacentCharacters", "int", "sso.version.version1", 0),
    ],
)
CreateDataType(
    "sso.admin.PasswordFormat.LengthRestriction",
    "SsoAdminPasswordFormatLengthRestriction",
    "vmodl.DynamicData",
    "sso.version.version1",
    [
        ("minLength", "int", "sso.version.version1", 0),
        ("maxLength", "int", "sso.version.version1", 0),
    ],
)
CreateDataType(
    "sso.admin.PasswordFormat.AlphabeticRestriction",
    "SsoAdminPasswordFormatAlphabeticRestriction",
    "vmodl.DynamicData",
    "sso.version.version1",
    [
        ("minAlphabeticCount", "int", "sso.version.version1", 0),
        ("minUppercaseCount", "int", "sso.version.version1", 0),
        ("minLowercaseCount", "int", "sso.version.version1", 0),
    ],
)
CreateDataType(
    "sso.admin.PasswordPolicy",
    "SsoAdminPasswordPolicy",
    "vmodl.DynamicData",
    "sso.version.version1",
    [
        ("description", "string", "sso.version.version1", F_OPTIONAL),
        ("prohibitedPreviousPasswordsCount", "int", "sso.version.version1", 0),
        ("passwordFormat", "sso.admin.PasswordFormat", "sso.version.version1", 0),
        ("passwordLifetimeDays", "int", "sso.version.version1", F_OPTIONAL),
    ],
)
CreateManagedType(
    "sso.admin.PasswordPolicyService",
    "SsoAdminPasswordPolicyService",
    "vmodl.ManagedObject",
    "sso.version.version1",
    None,
    [
        (
            "updateLocalPasswordPolicy",
            "UpdateLocalPasswordPolicy",
            "sso.version.version1",
            (("policy", "sso.admin.PasswordPolicy", "sso.version.version1", 0, None),),
            (0, "void", "void"),
            "Sso.AdminServer.Administer",
            [
                "sso.admin.fault.InvalidPasswordPolicyFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "getLocalPasswordPolicy",
            "GetLocalPasswordPolicy",
            "sso.version.version1",
            (),
            (0, "sso.admin.PasswordPolicy", "sso.admin.PasswordPolicy"),
            "Sso.Self.Administer",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
    ],
)
CreateDataType(
    "sso.admin.PersonDetails",
    "SsoAdminPersonDetails",
    "vmodl.DynamicData",
    "sso.version.version1",
    [
        ("description", "string", "sso.version.version1", F_OPTIONAL),
        ("emailAddress", "string", "sso.version.version1", F_OPTIONAL),
        ("firstName", "string", "sso.version.version1", F_OPTIONAL),
        ("lastName", "string", "sso.version.version1", F_OPTIONAL),
        ("userPrincipalName", "string", "sso.version.version2_5", F_OPTIONAL),
    ],
)
CreateDataType(
    "sso.admin.PersonUser",
    "SsoAdminPersonUser",
    "vmodl.DynamicData",
    "sso.version.version1",
    [
        ("id", "sso.PrincipalId", "sso.version.version1", 0),
        ("alias", "sso.PrincipalId", "sso.version.version1", F_OPTIONAL),
        ("details", "sso.admin.PersonDetails", "sso.version.version1", 0),
        ("disabled", "boolean", "sso.version.version1", 0),
        ("locked", "boolean", "sso.version.version1", 0),
    ],
)
CreateManagedType(
    "sso.admin.PrincipalDiscoveryService",
    "SsoAdminPrincipalDiscoveryService",
    "vmodl.ManagedObject",
    "sso.version.version1",
    None,
    [
        (
            "lookup",
            "Lookup",
            "sso.version.version1_5",
            (
                ("id", "sso.PrincipalId", "sso.version.version1_5", 0, None),
                ("isGroup", "boolean", "sso.version.version1_5", 0, None),
            ),
            (F_OPTIONAL, "sso.PrincipalId", "sso.PrincipalId"),
            "System.Read",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "findPersonUser",
            "FindPersonUser",
            "sso.version.version1",
            (("userId", "sso.PrincipalId", "sso.version.version1", 0, None),),
            (F_OPTIONAL, "sso.admin.PersonUser", "sso.admin.PersonUser"),
            "System.Read",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "findSelfPersonUser",
            "FindSelfPersonUser",
            "sso.version.version1_5",
            (),
            (0, "sso.admin.PersonUser", "sso.admin.PersonUser"),
            "Sso.Self.Administer",
            [
                "sso.fault.InvalidPrincipalFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "findSolutionUser",
            "FindSolutionUser",
            "sso.version.version1",
            (("userName", "string", "sso.version.version1", 0, None),),
            (F_OPTIONAL, "sso.admin.SolutionUser", "sso.admin.SolutionUser"),
            "System.Read",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "findSolutionUserByCertDN",
            "FindSolutionUserByCertDN",
            "sso.version.version1",
            (("certDN", "string", "sso.version.version1", 0, None),),
            (F_OPTIONAL, "sso.admin.SolutionUser", "sso.admin.SolutionUser"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "findUser",
            "FindUser",
            "sso.version.version1",
            (("userId", "sso.PrincipalId", "sso.version.version1", 0, None),),
            (F_OPTIONAL, "sso.admin.User", "sso.admin.User"),
            "System.Read",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "findGroup",
            "FindGroup",
            "sso.version.version1",
            (("groupId", "sso.PrincipalId", "sso.version.version1", 0, None),),
            (F_OPTIONAL, "sso.admin.Group", "sso.admin.Group"),
            "System.Read",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "findPersonUsers",
            "FindPersonUsers",
            "sso.version.version1",
            (
                (
                    "criteria",
                    "sso.admin.PrincipalDiscoveryService.SearchCriteria",
                    "sso.version.version1",
                    0,
                    None,
                ),
                ("limit", "int", "sso.version.version1", 0, None),
            ),
            (F_OPTIONAL, "sso.admin.PersonUser[]", "sso.admin.PersonUser[]"),
            "System.Read",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "findPersonUsersByName",
            "FindPersonUsersByName",
            "sso.version.version3",
            (
                (
                    "criteria",
                    "sso.admin.PrincipalDiscoveryService.SearchCriteria",
                    "sso.version.version3",
                    0,
                    None,
                ),
                ("limit", "int", "sso.version.version3", 0, None),
            ),
            (F_OPTIONAL, "sso.admin.PersonUser[]", "sso.admin.PersonUser[]"),
            "System.Read",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "findSolutionUsers",
            "FindSolutionUsers",
            "sso.version.version1",
            (
                ("searchString", "string", "sso.version.version1", 0, None),
                ("limit", "int", "sso.version.version1", 0, None),
            ),
            (F_OPTIONAL, "sso.admin.SolutionUser[]", "sso.admin.SolutionUser[]"),
            "System.Read",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "findUsers",
            "FindUsers",
            "sso.version.version1",
            (
                (
                    "criteria",
                    "sso.admin.PrincipalDiscoveryService.SearchCriteria",
                    "sso.version.version1",
                    0,
                    None,
                ),
                ("limit", "int", "sso.version.version1", 0, None),
            ),
            (F_OPTIONAL, "sso.admin.User[]", "sso.admin.User[]"),
            "System.Read",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "findUserAccount",
            "FindUserAccount",
            "sso.version.version2",
            (("userName", "string", "sso.version.version2", 0, None),),
            (
                0,
                "sso.admin.PrincipalDiscoveryService.SearchResult",
                "sso.admin.PrincipalDiscoveryService.SearchResult",
            ),
            "System.Read",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "findGroupAccount",
            "FindGroupAccount",
            "sso.version.version2",
            (("groupName", "string", "sso.version.version2", 0, None),),
            (F_OPTIONAL, "sso.admin.Group", "sso.admin.Group"),
            "System.Read",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "findGroups",
            "FindGroups",
            "sso.version.version1",
            (
                (
                    "criteria",
                    "sso.admin.PrincipalDiscoveryService.SearchCriteria",
                    "sso.version.version1",
                    0,
                    None,
                ),
                ("limit", "int", "sso.version.version1", 0, None),
            ),
            (F_OPTIONAL, "sso.admin.Group[]", "sso.admin.Group[]"),
            "System.Read",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "findGroupsByName",
            "FindGroupsByName",
            "sso.version.version3",
            (
                (
                    "criteria",
                    "sso.admin.PrincipalDiscoveryService.SearchCriteria",
                    "sso.version.version3",
                    0,
                    None,
                ),
                ("limit", "int", "sso.version.version3", 0, None),
            ),
            (F_OPTIONAL, "sso.admin.Group[]", "sso.admin.Group[]"),
            "System.Read",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "find",
            "Find",
            "sso.version.version1",
            (
                (
                    "criteria",
                    "sso.admin.PrincipalDiscoveryService.SearchCriteria",
                    "sso.version.version1",
                    0,
                    None,
                ),
                ("limit", "int", "sso.version.version1", 0, None),
            ),
            (
                0,
                "sso.admin.PrincipalDiscoveryService.SearchResult",
                "sso.admin.PrincipalDiscoveryService.SearchResult",
            ),
            "System.Read",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "findByName",
            "FindByName",
            "sso.version.version3",
            (
                (
                    "criteria",
                    "sso.admin.PrincipalDiscoveryService.SearchCriteria",
                    "sso.version.version3",
                    0,
                    None,
                ),
                ("limit", "int", "sso.version.version3", 0, None),
            ),
            (
                0,
                "sso.admin.PrincipalDiscoveryService.SearchResult",
                "sso.admin.PrincipalDiscoveryService.SearchResult",
            ),
            "System.Read",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "findUsersInGroup",
            "FindUsersInGroup",
            "sso.version.version1",
            (
                ("groupId", "sso.PrincipalId", "sso.version.version1", 0, None),
                ("searchString", "string", "sso.version.version1", 0, None),
                ("limit", "int", "sso.version.version1", 0, None),
            ),
            (F_OPTIONAL, "sso.admin.User[]", "sso.admin.User[]"),
            "System.Read",
            [
                "sso.fault.InvalidPrincipalFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "findPersonUsersByNameInGroup",
            "FindPersonUsersByNameInGroup",
            "sso.version.version3",
            (
                ("groupId", "sso.PrincipalId", "sso.version.version3", 0, None),
                ("searchString", "string", "sso.version.version3", 0, None),
                ("limit", "int", "sso.version.version3", 0, None),
            ),
            (F_OPTIONAL, "sso.admin.PersonUser[]", "sso.admin.PersonUser[]"),
            "System.Read",
            [
                "sso.fault.InvalidPrincipalFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "findPersonUsersInGroup",
            "FindPersonUsersInGroup",
            "sso.version.version1",
            (
                ("groupId", "sso.PrincipalId", "sso.version.version1", 0, None),
                ("searchString", "string", "sso.version.version1", 0, None),
                ("limit", "int", "sso.version.version1", 0, None),
            ),
            (F_OPTIONAL, "sso.admin.PersonUser[]", "sso.admin.PersonUser[]"),
            "System.Read",
            [
                "sso.fault.InvalidPrincipalFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "findSolutionUsersInGroup",
            "FindSolutionUsersInGroup",
            "sso.version.version1",
            (
                ("groupName", "string", "sso.version.version1", 0, None),
                ("searchString", "string", "sso.version.version1", 0, None),
                ("limit", "int", "sso.version.version1", 0, None),
            ),
            (F_OPTIONAL, "sso.admin.SolutionUser[]", "sso.admin.SolutionUser[]"),
            "System.Read",
            [
                "sso.fault.InvalidPrincipalFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "findGroupsInGroup",
            "FindGroupsInGroup",
            "sso.version.version1",
            (
                ("groupId", "sso.PrincipalId", "sso.version.version1", 0, None),
                ("searchString", "string", "sso.version.version1", 0, None),
                ("limit", "int", "sso.version.version1", 0, None),
            ),
            (F_OPTIONAL, "sso.admin.Group[]", "sso.admin.Group[]"),
            "System.Read",
            [
                "sso.fault.InvalidPrincipalFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "findGroupsByNameInGroup",
            "FindGroupsByNameInGroup",
            "sso.version.version3",
            (
                ("groupId", "sso.PrincipalId", "sso.version.version3", 0, None),
                ("searchString", "string", "sso.version.version3", 0, None),
                ("limit", "int", "sso.version.version3", 0, None),
            ),
            (F_OPTIONAL, "sso.admin.Group[]", "sso.admin.Group[]"),
            "System.Read",
            [
                "sso.fault.InvalidPrincipalFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "findDirectParentGroups",
            "FindDirectParentGroups",
            "sso.version.version1",
            (("principalId", "sso.PrincipalId", "sso.version.version1", 0, None),),
            (F_OPTIONAL, "sso.admin.Group[]", "sso.admin.Group[]"),
            "System.Read",
            [
                "sso.fault.InvalidPrincipalFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "findNestedParentGroups",
            "FindNestedParentGroups",
            "sso.version.version1",
            (("userId", "sso.PrincipalId", "sso.version.version1", 0, None),),
            (F_OPTIONAL, "sso.admin.Group[]", "sso.admin.Group[]"),
            "System.Read",
            [
                "sso.fault.InvalidPrincipalFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "findLockedUsers",
            "FindLockedUsers",
            "sso.version.version1",
            (
                ("searchString", "string", "sso.version.version1", 0, None),
                ("limit", "int", "sso.version.version1", 0, None),
            ),
            (F_OPTIONAL, "sso.admin.PersonUser[]", "sso.admin.PersonUser[]"),
            "System.Read",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "findDisabledPersonUsers",
            "FindDisabledPersonUsers",
            "sso.version.version1",
            (
                ("searchString", "string", "sso.version.version1", 0, None),
                ("limit", "int", "sso.version.version1", 0, None),
            ),
            (F_OPTIONAL, "sso.admin.PersonUser[]", "sso.admin.PersonUser[]"),
            "System.Read",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "findDisabledSolutionUsers",
            "FindDisabledSolutionUsers",
            "sso.version.version1",
            (("searchString", "string", "sso.version.version1", 0, None),),
            (F_OPTIONAL, "sso.admin.SolutionUser[]", "sso.admin.SolutionUser[]"),
            "System.Read",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "findRegisteredExternalIDPUser",
            "FindRegisteredExternalIDPUser",
            "sso.version.version2",
            (("userId", "sso.PrincipalId", "sso.version.version2", 0, None),),
            (F_OPTIONAL, "sso.admin.PersonUser", "sso.admin.PersonUser"),
            "System.Read",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "getImplicitGroupNames",
            "GetImplicitGroupNames",
            "sso.version.version2",
            (),
            (0, "string[]", "string[]"),
            "System.Anonymous",
            [
                "sso.fault.InvalidCredentials",
            ],
        ),
    ],
)
CreateDataType(
    "sso.admin.PrincipalDiscoveryService.SearchResult",
    "SsoAdminPrincipalDiscoveryServiceSearchResult",
    "vmodl.DynamicData",
    "sso.version.version1",
    [
        ("personUsers", "sso.admin.PersonUser[]", "sso.version.version1", F_OPTIONAL),
        (
            "solutionUsers",
            "sso.admin.SolutionUser[]",
            "sso.version.version1",
            F_OPTIONAL,
        ),
        ("groups", "sso.admin.Group[]", "sso.version.version1", F_OPTIONAL),
    ],
)
CreateDataType(
    "sso.admin.PrincipalDiscoveryService.SearchCriteria",
    "SsoAdminPrincipalDiscoveryServiceSearchCriteria",
    "vmodl.DynamicData",
    "sso.version.version1",
    [
        ("searchString", "string", "sso.version.version1", 0),
        ("domain", "string", "sso.version.version1", 0),
    ],
)
CreateManagedType(
    "sso.admin.PrincipalManagementService",
    "SsoAdminPrincipalManagementService",
    "vmodl.ManagedObject",
    "sso.version.version1",
    None,
    [
        (
            "createLocalPersonUser",
            "CreateLocalPersonUser",
            "sso.version.version1",
            (
                ("userName", "string", "sso.version.version1", 0, None),
                (
                    "userDetails",
                    "sso.admin.PersonDetails",
                    "sso.version.version1",
                    0,
                    None,
                ),
                ("password", "string", "sso.version.version1", F_SECRET, None),
            ),
            (0, "sso.PrincipalId", "sso.PrincipalId"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.InvalidPrincipalFault",
                "sso.admin.fault.PasswordPolicyViolationFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "createLocalSolutionUser",
            "CreateLocalSolutionUser",
            "sso.version.version1",
            (
                ("userName", "string", "sso.version.version1", 0, None),
                (
                    "userDetails",
                    "sso.admin.SolutionDetails",
                    "sso.version.version1",
                    0,
                    None,
                ),
                ("external", "boolean", "sso.version.version2", F_OPTIONAL, None),
            ),
            (0, "sso.PrincipalId", "sso.PrincipalId"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.InvalidPrincipalFault",
                "sso.admin.fault.DuplicateSolutionCertificateFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "createLocalGroup",
            "CreateLocalGroup",
            "sso.version.version1",
            (
                ("groupName", "string", "sso.version.version1", 0, None),
                (
                    "groupDetails",
                    "sso.admin.GroupDetails",
                    "sso.version.version1",
                    0,
                    None,
                ),
            ),
            (0, "sso.PrincipalId", "sso.PrincipalId"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.InvalidPrincipalFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "deleteLocalPrincipal",
            "DeleteLocalPrincipal",
            "sso.version.version1",
            (("principalName", "string", "sso.version.version1", 0, None),),
            (0, "void", "void"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.InvalidPrincipalFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "removeFromLocalGroup",
            "RemoveFromLocalGroup",
            "sso.version.version1",
            (
                ("principalId", "sso.PrincipalId", "sso.version.version1", 0, None),
                ("groupName", "string", "sso.version.version1", 0, None),
            ),
            (0, "boolean", "boolean"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.InvalidPrincipalFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "removePrincipalsFromLocalGroup",
            "RemovePrincipalsFromLocalGroup",
            "sso.version.version1",
            (
                ("principalsIds", "sso.PrincipalId[]", "sso.version.version1", 0, None),
                ("groupName", "string", "sso.version.version1", 0, None),
            ),
            (0, "boolean[]", "boolean[]"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.InvalidPrincipalFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "addUserToLocalGroup",
            "AddUserToLocalGroup",
            "sso.version.version1",
            (
                ("userId", "sso.PrincipalId", "sso.version.version1", 0, None),
                ("groupName", "string", "sso.version.version1", 0, None),
            ),
            (0, "boolean", "boolean"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.InvalidPrincipalFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "addUsersToLocalGroup",
            "AddUsersToLocalGroup",
            "sso.version.version1",
            (
                ("userIds", "sso.PrincipalId[]", "sso.version.version1", 0, None),
                ("groupName", "string", "sso.version.version1", 0, None),
            ),
            (0, "boolean[]", "boolean[]"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.InvalidPrincipalFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "addGroupToLocalGroup",
            "AddGroupToLocalGroup",
            "sso.version.version1",
            (
                ("groupId", "sso.PrincipalId", "sso.version.version1", 0, None),
                ("groupName", "string", "sso.version.version1", 0, None),
            ),
            (0, "boolean", "boolean"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.InvalidPrincipalFault",
                "sso.admin.fault.GroupCyclicDependencyFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "addGroupsToLocalGroup",
            "AddGroupsToLocalGroup",
            "sso.version.version1",
            (
                ("groupIds", "sso.PrincipalId[]", "sso.version.version1", 0, None),
                ("groupName", "string", "sso.version.version1", 0, None),
            ),
            (0, "boolean[]", "boolean[]"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.InvalidPrincipalFault",
                "sso.admin.fault.GroupCyclicDependencyFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "updateLocalPersonUserDetails",
            "UpdateLocalPersonUserDetails",
            "sso.version.version1",
            (
                ("userName", "string", "sso.version.version1", 0, None),
                (
                    "userDetails",
                    "sso.admin.PersonDetails",
                    "sso.version.version1",
                    0,
                    None,
                ),
            ),
            (0, "sso.PrincipalId", "sso.PrincipalId"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.InvalidPrincipalFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "resetLocalPersonUserPassword",
            "ResetLocalPersonUserPassword",
            "sso.version.version1",
            (
                ("userName", "string", "sso.version.version1", 0, None),
                ("newPassword", "string", "sso.version.version1", F_SECRET, None),
            ),
            (0, "void", "void"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.InvalidPrincipalFault",
                "sso.admin.fault.PasswordPolicyViolationFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "updateLocalSolutionUserDetails",
            "UpdateLocalSolutionUserDetails",
            "sso.version.version1",
            (
                ("userName", "string", "sso.version.version1", 0, None),
                (
                    "userDetails",
                    "sso.admin.SolutionDetails",
                    "sso.version.version1",
                    0,
                    None,
                ),
            ),
            (0, "sso.PrincipalId", "sso.PrincipalId"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.InvalidPrincipalFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "updateLocalGroupDetails",
            "UpdateLocalGroupDetails",
            "sso.version.version1",
            (
                ("groupName", "string", "sso.version.version1", 0, None),
                (
                    "groupDetails",
                    "sso.admin.GroupDetails",
                    "sso.version.version1",
                    0,
                    None,
                ),
            ),
            (0, "sso.PrincipalId", "sso.PrincipalId"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.InvalidPrincipalFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "updateSelfLocalPersonUserDetails",
            "UpdateSelfLocalPersonUserDetails",
            "sso.version.version1",
            (
                (
                    "userDetails",
                    "sso.admin.PersonDetails",
                    "sso.version.version1",
                    0,
                    None,
                ),
            ),
            (0, "sso.PrincipalId", "sso.PrincipalId"),
            "Sso.Self.Administer",
            [
                "sso.fault.InvalidPrincipalFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "deleteSelfSolutionUser",
            "DeleteSelfSolutionUser",
            "sso.version.version1",
            (),
            (0, "void", "void"),
            "Sso.Self.Administer",
            [
                "sso.fault.InvalidPrincipalFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "resetSelfLocalPersonUserPassword",
            "ResetSelfLocalPersonUserPassword",
            "sso.version.version1",
            (("newPassword", "string", "sso.version.version1", F_SECRET, None),),
            (0, "void", "void"),
            "Sso.Self.Administer",
            [
                "sso.fault.InvalidPrincipalFault",
                "sso.admin.fault.PasswordPolicyViolationFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "resetLocalUserPassword",
            "ResetLocalUserPassword",
            "sso.version.version1",
            (
                ("username", "string", "sso.version.version1", 0, None),
                ("currentPassword", "string", "sso.version.version1", F_SECRET, None),
                ("newPassword", "string", "sso.version.version1", F_SECRET, None),
            ),
            (0, "void", "void"),
            None,
            [
                "vmodl.fault.InvalidRequest",
                "sso.fault.InvalidPrincipalFault",
                "sso.admin.fault.PasswordPolicyViolationFault",
            ],
        ),
        (
            "updateSelfLocalSolutionUserDetails",
            "UpdateSelfLocalSolutionUserDetails",
            "sso.version.version1",
            (
                (
                    "userDetails",
                    "sso.admin.SolutionDetails",
                    "sso.version.version1",
                    0,
                    None,
                ),
            ),
            (0, "sso.PrincipalId", "sso.PrincipalId"),
            "Sso.Self.Administer",
            [
                "sso.fault.InvalidPrincipalFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "unlockUserAccount",
            "UnlockUserAccount",
            "sso.version.version1",
            (("userId", "sso.PrincipalId", "sso.version.version1", 0, None),),
            (0, "boolean", "boolean"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.InvalidPrincipalFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "enableUserAccount",
            "EnableUserAccount",
            "sso.version.version1",
            (("userId", "sso.PrincipalId", "sso.version.version1", 0, None),),
            (0, "boolean", "boolean"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.InvalidPrincipalFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "disableUserAccount",
            "DisableUserAccount",
            "sso.version.version1",
            (("userId", "sso.PrincipalId", "sso.version.version1", 0, None),),
            (0, "boolean", "boolean"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.InvalidPrincipalFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "getDaysRemainingUntilPasswordExpiration",
            "GetDaysRemainingUntilPasswordExpiration",
            "sso.version.version2",
            (("userId", "sso.PrincipalId", "sso.version.version2", 0, None),),
            (0, "int", "int"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.InvalidPrincipalFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "getDaysRemainingUntilSelfPasswordExpiration",
            "GetDaysRemainingUntilSelfPasswordExpiration",
            "sso.version.version2",
            (),
            (0, "int", "int"),
            "Sso.Self.Administer",
            [
                "sso.fault.InvalidPrincipalFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "registerExternalUser",
            "RegisterExternalUser",
            "sso.version.version2",
            (("externalUserId", "sso.PrincipalId", "sso.version.version2", 0, None),),
            (0, "boolean", "boolean"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.InvalidPrincipalFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "removeExternalUser",
            "RemoveExternalUser",
            "sso.version.version2",
            (("externalUserId", "sso.PrincipalId", "sso.version.version2", 0, None),),
            (0, "boolean", "boolean"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.InvalidPrincipalFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
    ],
)
CreateManagedType(
    "sso.admin.ReplicationService",
    "SsoAdminReplicationService",
    "vmodl.ManagedObject",
    "sso.version.version1",
    None,
    [
        (
            "exportFullState",
            "ExportFullState",
            "sso.version.version1",
            (),
            (0, "vmodl.Binary", "vmodl.Binary"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
                "vmodl.fault.NotSupported",
                "sso.fault.InternalFault",
            ],
        ),
        (
            "importFullState",
            "ImportFullState",
            "sso.version.version1",
            (("fullState", "vmodl.Binary", "sso.version.version1", 0, None),),
            (0, "void", "void"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
                "vmodl.fault.NotSupported",
                "vmodl.fault.InvalidArgument",
                "sso.fault.InternalFault",
            ],
        ),
    ],
)
CreateManagedType(
    "sso.admin.RoleManagementService",
    "SsoAdminRoleManagementService",
    "vmodl.ManagedObject",
    "sso.version.version1",
    None,
    [
        (
            "setRole",
            "SetRole",
            "sso.version.version1",
            (
                ("userId", "sso.PrincipalId", "sso.version.version1", 0, None),
                ("role", "string", "sso.version.version1", 0, None),
            ),
            (0, "boolean", "boolean"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.InvalidPrincipalFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "hasAdministratorRole",
            "HasAdministratorRole",
            "sso.version.version1",
            (("userId", "sso.PrincipalId", "sso.version.version1", 0, None),),
            (0, "boolean", "boolean"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.InvalidPrincipalFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "hasConfigurationUserRole",
            "HasConfigurationUserRole",
            "sso.version.version3_1",
            (("userId", "sso.PrincipalId", "sso.version.version3_1", 0, None),),
            (0, "boolean", "boolean"),
            "SystemConfiguration.Administrators",
            [
                "sso.fault.InvalidPrincipalFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "hasRegularUserRole",
            "HasRegularUserRole",
            "sso.version.version1",
            (("userId", "sso.PrincipalId", "sso.version.version1", 0, None),),
            (0, "boolean", "boolean"),
            "System.Read",
            [
                "sso.fault.InvalidPrincipalFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "grantWSTrustRole",
            "GrantWSTrustRole",
            "sso.version.version2",
            (
                ("userId", "sso.PrincipalId", "sso.version.version2", 0, None),
                ("role", "string", "sso.version.version2", 0, None),
            ),
            (0, "boolean", "boolean"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.InvalidPrincipalFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "revokeWSTrustRole",
            "RevokeWSTrustRole",
            "sso.version.version2",
            (
                ("userId", "sso.PrincipalId", "sso.version.version2", 0, None),
                ("role", "string", "sso.version.version2", 0, None),
            ),
            (0, "boolean", "boolean"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.InvalidPrincipalFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "grantIDPProvisioningRole",
            "GrantIDPProvisioningRole",
            "sso.version.version2",
            (
                ("userId", "sso.PrincipalId", "sso.version.version2", 0, None),
                ("role", "string", "sso.version.version2", 0, None),
            ),
            (0, "boolean", "boolean"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.InvalidPrincipalFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "revokeIDPProvisioningRole",
            "RevokeIDPProvisioningRole",
            "sso.version.version2",
            (
                ("userId", "sso.PrincipalId", "sso.version.version2", 0, None),
                ("role", "string", "sso.version.version2", 0, None),
            ),
            (0, "boolean", "boolean"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.InvalidPrincipalFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
    ],
)
CreateEnumType(
    "sso.admin.RoleManagementService.Role",
    "SsoAdminRoleManagementServiceRole",
    "sso.version.version1",
    [
        "GuestUser",
        "RegularUser",
        "ConfigurationUser",
        "IdentitySourceAdministrator",
        "Administrator",
    ],
)
CreateEnumType(
    "sso.admin.RoleManagementService.WSTrustRole",
    "SsoAdminRoleManagementServiceWSTrustRole",
    "sso.version.version2",
    ["ActAsUser"],
)
CreateEnumType(
    "sso.admin.RoleManagementService.IDPProvisioningRole",
    "SsoAdminRoleManagementServiceIDPProvisioningRole",
    "sso.version.version2",
    ["IDPAdministrator"],
)
CreateDataType(
    "sso.admin.ServiceContent",
    "SsoAdminServiceContent",
    "vmodl.DynamicData",
    "sso.version.version1",
    [
        ("aboutInfo", "sso.AboutInfo", "sso.version.version1", 0),
        ("sessionManager", "sso.SessionManager", "sso.version.version1", 0),
        (
            "configurationManagementService",
            "sso.admin.ConfigurationManagementService",
            "sso.version.version1",
            0,
        ),
        (
            "smtpManagementService",
            "sso.admin.SmtpManagementService",
            "sso.version.version1",
            0,
        ),
        (
            "principalDiscoveryService",
            "sso.admin.PrincipalDiscoveryService",
            "sso.version.version1",
            0,
        ),
        (
            "principalManagementService",
            "sso.admin.PrincipalManagementService",
            "sso.version.version1",
            0,
        ),
        (
            "roleManagementService",
            "sso.admin.RoleManagementService",
            "sso.version.version1",
            0,
        ),
        (
            "passwordPolicyService",
            "sso.admin.PasswordPolicyService",
            "sso.version.version1",
            0,
        ),
        (
            "lockoutPolicyService",
            "sso.admin.LockoutPolicyService",
            "sso.version.version1",
            0,
        ),
        (
            "domainManagementService",
            "sso.admin.DomainManagementService",
            "sso.version.version1",
            0,
        ),
        (
            "identitySourceManagementService",
            "sso.admin.IdentitySourceManagementService",
            "sso.version.version1_5",
            F_OPTIONAL,
        ),
        (
            "systemManagementService",
            "sso.admin.SystemManagementService",
            "sso.version.version1_5",
            F_OPTIONAL,
        ),
        (
            "computerManagementService",
            "sso.admin.ComputerManagementService",
            "sso.version.version3_1",
            F_OPTIONAL,
        ),
        (
            "ssoHealthManagementService",
            "sso.admin.SsoHealthManagementService",
            "sso.version.version3_5",
            F_OPTIONAL,
        ),
        (
            "deploymentInformationService",
            "sso.admin.DeploymentInformationService",
            "sso.version.version1",
            0,
        ),
        (
            "replicationService",
            "sso.admin.ReplicationService",
            "sso.version.version1",
            0,
        ),
    ],
)
CreateDataType(
    "sso.admin.ServiceEndpoint",
    "SsoAdminServiceEndpoint",
    "vmodl.DynamicData",
    "sso.version.version3",
    [
        ("name", "string", "sso.version.version3", 0),
        ("endpoint", "string", "sso.version.version3", 0),
        ("binding", "string", "sso.version.version3", 0),
    ],
)
CreateManagedType(
    "sso.admin.ServiceInstance",
    "SsoAdminServiceInstance",
    "vmodl.ManagedObject",
    "sso.version.version1",
    None,
    [
        (
            "retrieveServiceContent",
            "SsoAdminServiceInstance",
            "sso.version.version1",
            (),
            (0, "sso.admin.ServiceContent", "sso.admin.ServiceContent"),
            "System.Anonymous",
            [
                "sso.fault.InvalidCredentials",
            ],
        )
    ],
)
CreateDataType(
    "sso.admin.SmtpConfig",
    "SsoAdminSmtpConfig",
    "vmodl.DynamicData",
    "sso.version.version1",
    [
        ("host", "string", "sso.version.version1", F_OPTIONAL),
        ("port", "int", "sso.version.version1", F_OPTIONAL),
        ("authenticate", "boolean", "sso.version.version1", F_OPTIONAL),
        ("user", "string", "sso.version.version1", F_OPTIONAL),
        ("password", "string", "sso.version.version1", F_OPTIONAL),
    ],
)
CreateManagedType(
    "sso.admin.SmtpManagementService",
    "SsoAdminSmtpManagementService",
    "vmodl.ManagedObject",
    "sso.version.version1",
    None,
    [
        (
            "getSmtpConfiguration",
            "GetSmtpConfiguration",
            "sso.version.version1",
            (),
            (0, "sso.admin.SmtpConfig", "sso.admin.SmtpConfig"),
            "Sso.AdminServer.Administer",
            [
                "sso.admin.fault.SmtpConfigNotSetFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "updateSmtpConfiguration",
            "UpdateSmtpConfiguration",
            "sso.version.version1",
            (("config", "sso.admin.SmtpConfig", "sso.version.version1", 0, None),),
            (0, "void", "void"),
            "Sso.AdminServer.Administer",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "sendMail",
            "SendMail",
            "sso.version.version1",
            (("content", "sso.admin.MailContent", "sso.version.version1", 0, None),),
            (0, "void", "void"),
            "Sso.AdminServer.Administer",
            [
                "sso.admin.fault.SmtpConfigNotSetFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
    ],
)
CreateDataType(
    "sso.admin.SolutionDetails",
    "SsoAdminSolutionDetails",
    "vmodl.DynamicData",
    "sso.version.version1",
    [
        ("description", "string", "sso.version.version1", F_OPTIONAL),
        ("certificate", "string", "sso.version.version1", 0),
    ],
)
CreateDataType(
    "sso.admin.SolutionUser",
    "SsoAdminSolutionUser",
    "vmodl.DynamicData",
    "sso.version.version1",
    [
        ("id", "sso.PrincipalId", "sso.version.version1", 0),
        ("alias", "sso.PrincipalId", "sso.version.version1", F_OPTIONAL),
        ("details", "sso.admin.SolutionDetails", "sso.version.version1", 0),
        ("disabled", "boolean", "sso.version.version1", 0),
        ("external", "boolean", "sso.version.version2_5", 0),
    ],
)
CreateManagedType(
    "sso.admin.SsoHealthManagementService",
    "SsoAdminSsoHealthManagementService",
    "vmodl.ManagedObject",
    "sso.version.version3_5",
    None,
    [
        (
            "getSsoStatistics",
            "GetSsoStatistics",
            "sso.version.version3_5",
            (),
            (0, "sso.admin.SsoHealthStats", "sso.admin.SsoHealthStats"),
            "SystemConfiguration.Administrators",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        )
    ],
)
CreateDataType(
    "sso.admin.SsoHealthStats",
    "SsoAdminSsoHealthStats",
    "vmodl.DynamicData",
    "sso.version.version3_5",
    [
        ("tenant", "string", "sso.version.version3_5", 0),
        ("totalTokensGenerated", "int", "sso.version.version3_5", 0),
        ("totalTokensRenewed", "int", "sso.version.version3_5", 0),
        ("generatedTokensForTenant", "int", "sso.version.version3_5", 0),
        ("renewedTokensForTenant", "int", "sso.version.version3_5", 0),
        ("uptimeIDM", "long", "sso.version.version3_5", 0),
        ("uptimeSTS", "long", "sso.version.version3_5", 0),
    ],
)
CreateManagedType(
    "sso.admin.SystemManagementService",
    "SsoAdminSystemManagementService",
    "vmodl.ManagedObject",
    "sso.version.version1_5",
    None,
    [
        (
            "getActiveDirectoryJoinStatus",
            "IdS_getActiveDirectoryJoinStatus",
            "sso.version.version1_5",
            (),
            (
                0,
                "sso.admin.ActiveDirectoryJoinInfo",
                "sso.admin.ActiveDirectoryJoinInfo",
            ),
            "System.Read",
            [
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "joinActiveDirectory",
            "JoinActiveDirectory",
            "sso.version.version3_1",
            (
                ("username", "string", "sso.version.version3_1", 0, None),
                ("password", "string", "sso.version.version3_1", 0, None),
                ("domain", "string", "sso.version.version3_1", 0, None),
                ("orgUnit", "string", "sso.version.version3_1", F_OPTIONAL, None),
            ),
            (0, "void", "void"),
            "Sso.AdminServer.Administer",
            [
                "sso.admin.fault.ADDomainAccessDeniedFault",
                "sso.admin.fault.ADDomainUnknownDomainFault",
                "sso.admin.fault.ADDomainAlreadyJoinedFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
            ],
        ),
        (
            "leaveActiveDirectory",
            "LeaveActiveDirectory",
            "sso.version.version3_1",
            (
                ("username", "string", "sso.version.version3_1", 0, None),
                ("password", "string", "sso.version.version3_1", 0, None),
            ),
            (0, "void", "void"),
            "Sso.AdminServer.Administer",
            [
                "sso.admin.fault.ADIDSAlreadyExistFault",
                "sso.admin.fault.ADDomainAccessDeniedFault",
                "sso.admin.fault.ADDomainUnknownDomainFault",
                "sso.admin.fault.ADDomainNotJoinedFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
            ],
        ),
    ],
)
CreateDataType(
    "sso.admin.TrustedSTSConfig",
    "SsoAdminTrustedSTSConfig",
    "vmodl.DynamicData",
    "sso.version.version2",
    [
        ("issuer", "string", "sso.version.version2", 0),
        (
            "signingCertChain",
            "sso.admin.ConfigurationManagementService.CertificateChain",
            "sso.version.version2",
            0,
        ),
        (
            "subjectFormatMappings",
            "sso.admin.ConfigurationManagementService.AttributeConfig[]",
            "sso.version.version2",
            F_OPTIONAL,
        ),
        (
            "tokenClaimGroupMappings",
            "sso.admin.ConfigurationManagementService.TokenClaimGroupMapping[]",
            "sso.version.version3_5",
            F_OPTIONAL,
        ),
    ],
)
CreateDataType(
    "sso.admin.User",
    "SsoAdminUser",
    "vmodl.DynamicData",
    "sso.version.version1",
    [
        ("id", "sso.PrincipalId", "sso.version.version1", 0),
        ("alias", "sso.PrincipalId", "sso.version.version1", F_OPTIONAL),
        ("kind", "string", "sso.version.version1", 0),
        ("description", "string", "sso.version.version1", F_OPTIONAL),
    ],
)
CreateEnumType(
    "sso.admin.User.Kind",
    "SsoAdminUserKind",
    "sso.version.version1",
    ["person", "solution"],
)
CreateDataType(
    "sso.admin.VmHost",
    "SsoAdminVmHost",
    "vmodl.DynamicData",
    "sso.version.version3_1",
    [
        ("hostName", "string", "sso.version.version3_1", 0),
        ("domainController", "boolean", "sso.version.version3_1", 0),
    ],
)
CreateDataType(
    "sso.fault.InvalidCredentials",
    "SsoFaultInvalidCredentials",
    "vmodl.fault.SecurityError",
    "sso.version.version1",
    None,
)
CreateDataType(
    "sso.fault.NoPermission",
    "SsoFaultNoPermission",
    "vmodl.fault.SecurityError",
    "sso.version.version1",
    None,
)
CreateDataType(
    "sso.fault.NotAuthenticated",
    "SsoFaultNotAuthenticated",
    "vmodl.fault.SecurityError",
    "sso.version.version1",
    None,
)
CreateDataType(
    "sso.fault.RuntimeServiceFault",
    "SsoFaultRuntimeServiceFault",
    "vmodl.RuntimeFault",
    "sso.version.version1",
    None,
)
CreateDataType(
    "sso.fault.ServiceFault",
    "SsoFaultServiceFault",
    "vmodl.MethodFault",
    "sso.version.version1",
    None,
)
CreateManagedType(
    "sso.groupcheck.GroupCheckService",
    "SsoGroupcheckGroupCheckService",
    "vmodl.ManagedObject",
    "sso.version.version1",
    None,
    [
        (
            "isMemberOfGroup",
            "IsMemberOfGroup",
            "sso.version.version1",
            (
                ("userId", "sso.PrincipalId", "sso.version.version1", 0, None),
                ("groupId", "sso.PrincipalId", "sso.version.version1", 0, None),
            ),
            (0, "boolean", "boolean"),
            "System.Read",
            [
                "sso.fault.InvalidPrincipalFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "findParentGroups",
            "FindParentGroups",
            "sso.version.version1",
            (
                ("userId", "sso.PrincipalId", "sso.version.version1", 0, None),
                (
                    "groupList",
                    "sso.PrincipalId[]",
                    "sso.version.version1",
                    F_OPTIONAL,
                    None,
                ),
            ),
            (F_OPTIONAL, "sso.PrincipalId[]", "sso.PrincipalId[]"),
            "System.Read",
            [
                "sso.fault.InvalidPrincipalFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
        (
            "findAllParentGroups",
            "FindAllParentGroups",
            "sso.version.version1",
            (("userId", "sso.PrincipalId", "sso.version.version1", 0, None),),
            (F_OPTIONAL, "sso.PrincipalId[]", "sso.PrincipalId[]"),
            "System.Read",
            [
                "sso.fault.InvalidPrincipalFault",
                "sso.fault.NotAuthenticated",
                "sso.fault.NoPermission",
                "sso.fault.InvalidCredentials",
            ],
        ),
    ],
)
CreateDataType(
    "sso.groupcheck.ServiceContent",
    "SsoGroupcheckServiceContent",
    "vmodl.DynamicData",
    "sso.version.version1",
    [
        ("aboutInfo", "sso.AboutInfo", "sso.version.version1", 0),
        ("sessionManager", "sso.SessionManager", "sso.version.version1", 0),
        (
            "groupCheckService",
            "sso.groupcheck.GroupCheckService",
            "sso.version.version1",
            0,
        ),
    ],
)
CreateManagedType(
    "sso.groupcheck.ServiceInstance",
    "SsoGroupcheckServiceInstance",
    "vmodl.ManagedObject",
    "sso.version.version1",
    None,
    [
        (
            "retrieveServiceContent",
            "SsoGroupcheckServiceInstance",
            "sso.version.version1",
            (),
            (0, "sso.groupcheck.ServiceContent", "sso.groupcheck.ServiceContent"),
            "System.Anonymous",
            [
                "sso.fault.InvalidCredentials",
            ],
        )
    ],
)
CreateDataType(
    "sso.admin.fault.ADDomainAccessDeniedFault",
    "SsoAdminFaultADDomainAccessDeniedFault",
    "sso.fault.ServiceFault",
    "sso.version.version3_1",
    [
        ("domain", "string", "sso.version.version3_1", F_OPTIONAL),
        ("username", "string", "sso.version.version3_1", 0),
    ],
)
CreateDataType(
    "sso.admin.fault.ADDomainAlreadyJoinedFault",
    "SsoAdminFaultADDomainAlreadyJoinedFault",
    "sso.fault.ServiceFault",
    "sso.version.version3_1",
    None,
)
CreateDataType(
    "sso.admin.fault.ADDomainNotJoinedFault",
    "SsoAdminFaultADDomainNotJoinedFault",
    "sso.fault.ServiceFault",
    "sso.version.version3_1",
    None,
)
CreateDataType(
    "sso.admin.fault.ADDomainUnknownDomainFault",
    "SsoAdminFaultADDomainUnknownDomainFault",
    "sso.fault.ServiceFault",
    "sso.version.version3_1",
    [("domain", "string", "sso.version.version3_1", F_OPTIONAL)],
)
CreateDataType(
    "sso.admin.fault.ADIDSAlreadyExistFault",
    "SsoAdminFaultADIDSAlreadyExistFault",
    "sso.fault.ServiceFault",
    "sso.version.version1_5",
    [("domainName", "string", "sso.version.version1_5", 0)],
)
CreateDataType(
    "sso.admin.fault.CertChainInvalidTrustedPathFault",
    "SsoAdminFaultCertChainInvalidTrustedPathFault",
    "sso.fault.ServiceFault",
    "sso.version.version3",
    [("issuerName", "string", "sso.version.version3", 0)],
)
CreateDataType(
    "sso.admin.fault.CertificateDeletionFault",
    "SsoAdminFaultCertificateDeletionFault",
    "sso.fault.ServiceFault",
    "sso.version.version1_5",
    [("certificate", "string", "sso.version.version1_5", 0)],
)
CreateDataType(
    "sso.admin.fault.DirectoryServiceConnectionFault",
    "SsoAdminFaultDirectoryServiceConnectionFault",
    "sso.fault.ServiceFault",
    "sso.version.version1",
    [("uri", "vmodl.URI", "sso.version.version1", 0)],
)
CreateDataType(
    "sso.admin.fault.DomainManagerFault",
    "SsoAdminFaultDomainManagerFault",
    "sso.fault.RuntimeServiceFault",
    "sso.version.version1_5",
    [
        ("domainName", "string", "sso.version.version1_5", 0),
        ("errorCode", "int", "sso.version.version1_5", F_OPTIONAL),
    ],
)
CreateDataType(
    "sso.admin.fault.DomainNotFoundFault",
    "SsoAdminFaultDomainNotFoundFault",
    "sso.fault.ServiceFault",
    "sso.version.version1",
    [("domainName", "string", "sso.version.version1", 0)],
)
CreateDataType(
    "sso.admin.fault.DuplicateDataFault",
    "SsoAdminFaultDuplicateDataFault",
    "sso.fault.ServiceFault",
    "sso.version.version1",
    None,
)
CreateDataType(
    "sso.admin.fault.DuplicateDomainNameFault",
    "SsoAdminFaultDuplicateDomainNameFault",
    "sso.fault.ServiceFault",
    "sso.version.version1",
    [
        ("domainName", "string", "sso.version.version1", 0),
        ("domainAlias", "string", "sso.version.version1_5", F_OPTIONAL),
    ],
)
CreateDataType(
    "sso.admin.fault.DuplicateSolutionCertificateFault",
    "SsoAdminFaultDuplicateSolutionCertificateFault",
    "sso.fault.ServiceFault",
    "sso.version.version1",
    None,
)
CreateDataType(
    "sso.admin.fault.ExternalSTSCertChainInvalidTrustedPathFault",
    "SsoAdminFaultExternalSTSCertChainInvalidTrustedPathFault",
    "sso.fault.ServiceFault",
    "sso.version.version2",
    [("issuerName", "string", "sso.version.version2", 0)],
)
CreateDataType(
    "sso.admin.fault.ExternalSTSExtraneousCertsInCertChainFault",
    "SsoAdminFaultExternalSTSExtraneousCertsInCertChainFault",
    "sso.fault.ServiceFault",
    "sso.version.version2",
    [("issuerName", "string", "sso.version.version2", 0)],
)
CreateDataType(
    "sso.admin.fault.ExtraneousCertsInCertChainFault",
    "SsoAdminFaultExtraneousCertsInCertChainFault",
    "sso.fault.ServiceFault",
    "sso.version.version3",
    [("issuerName", "string", "sso.version.version3", 0)],
)
CreateDataType(
    "sso.admin.fault.GroupCyclicDependencyFault",
    "SsoAdminFaultGroupCyclicDependencyFault",
    "sso.fault.ServiceFault",
    "sso.version.version1",
    [
        ("groupBeingAdded", "string", "sso.version.version1", 0),
        ("existingGroup", "string", "sso.version.version1", 0),
    ],
)
CreateDataType(
    "sso.admin.fault.HostNotJoinedRequiredDomainFault",
    "SsoAdminFaultHostNotJoinedRequiredDomainFault",
    "sso.fault.RuntimeServiceFault",
    "sso.version.version1_5",
    [
        ("requiredDomainName", "string", "sso.version.version1_5", 0),
        ("joinedDomainName", "string", "sso.version.version1_5", F_OPTIONAL),
    ],
)
CreateDataType(
    "sso.admin.fault.InvalidPasswordPolicyFault",
    "SsoAdminFaultInvalidPasswordPolicyFault",
    "sso.fault.ServiceFault",
    "sso.version.version1",
    None,
)
CreateDataType(
    "sso.admin.fault.InvalidProviderFault",
    "SsoAdminFaultInvalidProviderFault",
    "sso.fault.RuntimeServiceFault",
    "sso.version.version1",
    [
        ("fieldName", "string", "sso.version.version1", 0),
        ("fieldValue", "string", "sso.version.version1", F_OPTIONAL),
    ],
)
CreateDataType(
    "sso.admin.fault.LocalOSDomainRegistrationFault",
    "SsoAdminFaultLocalOSDomainRegistrationFault",
    "sso.fault.RuntimeServiceFault",
    "sso.version.version1",
    None,
)
CreateDataType(
    "sso.admin.fault.NativeADRegistrationFault",
    "SsoAdminFaultNativeADRegistrationFault",
    "sso.fault.RuntimeServiceFault",
    "sso.version.version1_5",
    None,
)
CreateDataType(
    "sso.admin.fault.NoSuchConfigFault",
    "SsoAdminFaultNoSuchConfigFault",
    "sso.fault.ServiceFault",
    "sso.version.version3",
    [("issuerName", "string", "sso.version.version3", 0)],
)
CreateDataType(
    "sso.admin.fault.NoSuchExternalSTSConfigFault",
    "SsoAdminFaultNoSuchExternalSTSConfigFault",
    "sso.fault.ServiceFault",
    "sso.version.version2",
    [("issuerName", "string", "sso.version.version2", 0)],
)
CreateDataType(
    "sso.admin.fault.NoSuchRelyingPartyFault",
    "SsoAdminFaultNoSuchRelyingPartyFault",
    "sso.fault.ServiceFault",
    "sso.version.version2",
    [("relyingPartyName", "string", "sso.version.version2", 0)],
)
CreateDataType(
    "sso.admin.fault.PasswordPolicyViolationFault",
    "SsoAdminFaultPasswordPolicyViolationFault",
    "sso.fault.ServiceFault",
    "sso.version.version1",
    None,
)
CreateDataType(
    "sso.admin.fault.SmtpConfigNotSetFault",
    "SsoAdminFaultSmtpConfigNotSetFault",
    "sso.fault.ServiceFault",
    "sso.version.version1",
    None,
)
CreateDataType(
    "sso.fault.InternalFault",
    "SsoFaultInternalFault",
    "sso.fault.RuntimeServiceFault",
    "sso.version.version1",
    None,
)
CreateDataType(
    "sso.fault.InvalidPrincipalFault",
    "SsoFaultInvalidPrincipalFault",
    "sso.fault.ServiceFault",
    "sso.version.version1",
    [("principal", "string", "sso.version.version1", 0)],
)
CreateDataType(
    "sso.fault.NoDomainSearchPermission",
    "SsoFaultNoDomainSearchPermission",
    "sso.fault.RuntimeServiceFault",
    "sso.version.version1_5",
    [("domainName", "string", "sso.version.version2", F_OPTIONAL)],
)
