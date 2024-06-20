# **********************************************************
# Copyright 2005-2018 VMware, Inc.  All rights reserved. -- VMware Confidential
# **********************************************************
from . import CoreTypes
from . import QueryTypes

# pylint: skip-file

try:
    from . import ReflectTypes
except ImportError:
    pass
try:
    from . import ServerObjects
except ImportError:
    pass
try:
    from . import InternalServerObjects
except ImportError:
    pass

# Import all the known product-specific types
# XXX: Make this search the package for types?
try:
    from . import DrObjects
except ImportError:
    pass

try:
    from . import DrextObjects
except ImportError:
    pass

try:
    from . import HbrReplicaTypes
except ImportError:
    pass
try:
    from . import HmsdrsObjects
except ImportError:
    pass
try:
    from . import HostdObjects
except ImportError:
    pass
try:
    from . import VpxObjects
except ImportError:
    pass
try:
    from . import VorbTypes
except ImportError:
    pass
try:
    from . import DodoTypes
except ImportError:
    pass
try:
    from . import VmwauthproxyTypes
except ImportError:
    pass
try:
    from . import DmsTypes
except ImportError:
    pass
try:
    from . import OmsTypes
except ImportError:
    pass
try:
    from . import HmoTypes
except ImportError:
    pass
try:
    from . import CimsfccTypes
except ImportError:
    pass
try:
    from . import TaskupdaterTypes
except ImportError:
    pass
try:
    from . import ImgFactTypes
except ImportError:
    pass
try:
    from . import ImgBldTypes
except ImportError:
    pass
try:
    from . import VpxapiTypes
except ImportError:
    pass
try:
    from . import CsiObjects
except ImportError:
    pass

try:
    from . import HostdTypes
except ImportError:
    pass

try:
    from . import TaggingObjects
except ImportError:
    pass

try:
    from . import NfcTypes
except ImportError:
    pass

try:
    from . import SmsObjects
except ImportError:
    pass

try:
    from . import SpsObjects
except ImportError:
    pass

try:
    from . import DataserviceObjects
except ImportError:
    pass

# Start of update manager specific types
try:
    from . import IntegrityObjects
except ImportError:
    pass

try:
    from . import SysimageObjects
except ImportError:
    pass
# End of update manager specific types

try:
    from . import RbdTypes
except ImportError:
    pass

# Import Profile based management specific VMODL
try:
    from . import PbmObjects
except ImportError:
    pass

# Import VMODL based VASA definitions
try:
    from . import VasaObjects
except ImportError:
    pass

try:
    from . import CeipTypes
except ImportError:
    pass

try:
    from . import CisLicenseTypes
except ImportError:
    pass

try:
    from . import LegacyLicenseTypes
except ImportError:
    pass

try:
    from . import TestTypes
except ImportError:
    pass

try:
    from . import SsoTypes
except ImportError:
    pass

try:
    from . import CisCmTypes
except ImportError:
    pass

try:
    from . import CisDataTypes
except ImportError:
    pass

try:
    from . import DataserviceTypes
except ImportError:
    pass

try:
    from . import LookupTypes
except ImportError:
    pass

try:
    from . import VsanDpTypes
except ImportError:
    pass

try:
    from . import VslmObjects
except ImportError:
    pass
