# **********************************************************
# Copyright 2005-2016 VMware, Inc.  All rights reserved. -- VMware Confidential
# **********************************************************
# In VmomiSupport, to support dynamic type loading, all the data types are wrapped around
# using a meta type which can intercept attribute access and load the necessary nested
# classes. This can be implemented only in python 2.5 version or more.
import sys

if sys.version_info < (2, 5):
    sys.stderr.write("You need Python 2.5 or later to import pyVmomi module\n")
    sys.exit(1)

from . import VmomiSupport

from . import __bindings

# All data object types and fault types have DynamicData as an ancestor
# As well load it proactively.
# Note: This should be done before importing SoapAdapter as it uses
# some fault types
VmomiSupport.GetVmodlType("vmodl.DynamicData")

from .SoapAdapter import (
    SoapStubAdapter,
    StubAdapterBase,
    SoapCmdStubAdapter,
    SessionOrientedStub,
    ThumbprintMismatchException,
)

types = VmomiSupport.types

# This will allow files to use Create** functions
# directly from pyVmomi
CreateEnumType = VmomiSupport.CreateEnumType
CreateDataType = VmomiSupport.CreateDataType
CreateManagedType = VmomiSupport.CreateManagedType

# For all the top level names, creating a LazyModule object
# in the global namespace of pyVmomi. Files can just import the
# top level namespace and we will figure out what to load and when
# Examples:
# ALLOWED: from pyVmomi import vim
# NOT ALLOWED: from pyVmomi import vim.host
_globals = globals()
for name in VmomiSupport._topLevelNames:
    upperCaseName = VmomiSupport.Capitalize(name)
    obj = VmomiSupport.LazyModule(name)
    _globals[name] = obj
    if VmomiSupport._allowCapitalizedNames:
        _globals[upperCaseName] = obj
    if not hasattr(VmomiSupport.types, name):
        setattr(VmomiSupport.types, name, obj)
        if VmomiSupport._allowCapitalizedNames:
            setattr(VmomiSupport.types, upperCaseName, obj)
del _globals
