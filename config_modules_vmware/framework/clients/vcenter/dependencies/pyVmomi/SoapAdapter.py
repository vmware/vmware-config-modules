# **********************************************************
# Copyright 2005-2018 VMware, Inc.  All rights reserved. -- VMware Confidential
# **********************************************************
import base64
import contextlib
import copy
import os
import platform
import re
import socket
import subprocess  # nosec
import sys
import time
from datetime import datetime
from io import StringIO
from urllib.parse import urlparse
from xml.parsers.expat import ExpatError
from xml.parsers.expat import ParserCreate

import six
from six import PY2
from six import u

from . import Iso8601
from .StubAdapterAccessorImpl import StubAdapterAccessorMixin
from .VmomiSupport import *

# For Visor, space is very limited. Import xml.sax pull in too many junk.
# Define our own xml escape instead
# from xml.sax.saxutils import escape

try:
    import urllib.parse as urllib
except:
    import urllib

try:
    USERWORLD = os.uname()[0] == "VMkernel"
except:
    USERWORLD = False

# Timeout value used for idle connections in client connection pool.
# Default value is 900 seconds (15 minutes).
CONNECTION_POOL_IDLE_TIMEOUT_SEC = 900

NS_SEP = " "

XML_ENCODING = "UTF-8"
XML_HEADER = '<?xml version="1.0" encoding="%s"?>' % XML_ENCODING

XMLNS_SOAPENC = "http://schemas.xmlsoap.org/soap/encoding/"
XMLNS_SOAPENV = "http://schemas.xmlsoap.org/soap/envelope/"

XSI_TYPE = XMLNS_XSI + NS_SEP + "type"

# Note: Must make a copy to use the SOAP_NSMAP
# TODO: Change to frozendict, if available
SOAP_NSMAP = {
    XMLNS_SOAPENC: "soapenc",
    XMLNS_SOAPENV: "soapenv",
    XMLNS_XSI: "xsi",
    XMLNS_XSD: "xsd",
}

SOAP_ENVELOPE_TAG = "%s:Envelope" % SOAP_NSMAP[XMLNS_SOAPENV]
SOAP_HEADER_TAG = "%s:Header" % SOAP_NSMAP[XMLNS_SOAPENV]
SOAP_FAULT_TAG = "%s:Fault" % SOAP_NSMAP[XMLNS_SOAPENV]
SOAP_BODY_TAG = "%s:Body" % SOAP_NSMAP[XMLNS_SOAPENV]

SOAP_ENVELOPE_START = (
    "<%s " % SOAP_ENVELOPE_TAG
    + " ".join(["xmlns:" + prefix + '="' + urn + '"' for urn, prefix in six.iteritems(SOAP_NSMAP)])
    + ">\n"
)
SOAP_ENVELOPE_END = "\n</%s>" % (SOAP_ENVELOPE_TAG)
SOAP_HEADER_START = "<%s>" % SOAP_HEADER_TAG
SOAP_HEADER_END = "</%s>" % SOAP_HEADER_TAG
SOAP_BODY_START = "<%s>" % SOAP_BODY_TAG
SOAP_BODY_END = "</%s>" % SOAP_BODY_TAG
SOAP_START = SOAP_ENVELOPE_START + SOAP_BODY_START + "\n"
SOAP_END = "\n" + SOAP_BODY_END + SOAP_ENVELOPE_END

WSSE_PREFIX = "wsse"
WSSE_HEADER_TAG = "%s:Security" % WSSE_PREFIX
WSSE_NS_URL = "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"
WSSE_NS = 'xmlns:%s="%s"' % (WSSE_PREFIX, WSSE_NS_URL)
WSSE_HEADER_START = "<%s %s>" % (WSSE_HEADER_TAG, WSSE_NS)
WSSE_HEADER_END = "</%s>" % WSSE_HEADER_TAG

## MethodFault type
MethodFault = GetVmodlType("vmodl.MethodFault")
## Localized MethodFault type
LocalizedMethodFault = GetVmodlType("vmodl.LocalizedMethodFault")

# These info are included in the http user-agent header
# platform.uname() is doing fork() + exec(), so we prefer to avoid it on vmkernel. Causing MemSpike
# platform.uname() is retained to support Windows platform
PYTHON_VERSION = sys.version.split(" (")[0]
try:
    OS_INFO = os.uname()
    OS_NAME = OS_INFO[0]
    OS_VERSION = OS_INFO[2]
    OS_ARCH = OS_INFO[4]
except:
    PLATFORM_INFO = platform.uname()
    OS_NAME = PLATFORM_INFO[0]
    OS_VERSION = PLATFORM_INFO[2]
    OS_ARCH = PLATFORM_INFO[4]

# pylint: skip-file


## Thumbprint mismatch exception
#
class ThumbprintMismatchException(Exception):
    def __init__(self, expected, actual):
        Exception.__init__(
            self,
            "Server has wrong SHA thumbprint: %s " "(required) != %s (server)" % (expected, actual),
        )

        self.expected = expected
        self.actual = actual


## Escape <, >, &
def XmlEscape(xmlStr):
    escaped = xmlStr.replace("&", "&amp;").replace(">", "&gt;").replace("<", "&lt;")
    return escaped


## Clone SSLContext
## context.load_cert_chain(key_file, cert_file) is not thread safe
## Creating local context and assigning all paramters to context
# @param key_file The SSL key file to use when wrapping the socket.
# @param cert_file The SSL certificate file to use when wrapping the socket.
# @param context SSL Context describing the various SSL options. It is only
#                   supported in Python 2.7.9 or higher.
def _CloneSSLContext(context, certFile=None, certKeyFile=None):
    sslContext = ssl.create_default_context()
    sslContext.check_hostname = context.check_hostname
    sslContext.verify_mode = context.verify_mode
    if certFile and certKeyFile:
        sslContext.load_cert_chain(certFile, certKeyFile)
    return sslContext


# Validate IPv4 IP Pattern
# @param ip string ipv4 ip value to validate with IP pattern
# @return True if ip is IPv4 address, else False
def _CheckIPv4(ip):
    ipv4_pattern = re.compile("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
    return True if ipv4_pattern.match(ip) else False


# Validate IPv6 IP pattern
# @param ip string ipv6 ip value to validate with IP pattern
# @return True if ip is IPv6 address, else False
def _CheckIPv6(ip):
    ipv6_pattern = re.compile("[:a-fA-F0-9]*:[:a-fA-F0-9]*:[:a-fA-F0-9.]*?$")
    return True if ipv6_pattern.match(ip) else False


# Validate Hostname Pattern
# @param hostname string hostname value to validate with IP pattern
# @return True if hostname is hostname address, else False
def _CheckHostname(hostname):
    hostname_pattern = re.compile("[a-z0-9A-Z-]+[\.a-z0-9A-Z-]+$")
    return True if hostname_pattern.match(hostname) else False


## Get the start tag, end tag, and text handlers of a class
def GetHandlers(obj):
    return (
        obj.StartElementHandler,
        obj.EndElementHandler,
        obj.CharacterDataHandler,
        obj.StartNamespaceDeclHandler,
        obj.EndNamespaceDeclHandler,
    )


## Set the start tag, end tag, and text handlers of a parser
def SetHandlers(obj, handlers):
    (
        obj.StartElementHandler,
        obj.EndElementHandler,
        obj.CharacterDataHandler,
        obj.StartNamespaceDeclHandler,
        obj.EndNamespaceDeclHandler,
    ) = handlers


## Serialize an object to bytes
#
# This function assumes CheckField(info, val) was already called
# @param val the value to serialize
# @param info the field
# @param version the version
# @param nsMap a dict of xml ns -> prefix
# @return the serialized object as bytes
# @param encoding Deprecated this is not used during serialization since we always
#        use utf-8 to encode a request message. We didn't remove the
#        parameter so it is still compatible with clients that are still using it.
def Serialize(val, info=None, version=None, nsMap=None, encoding=None, hidepasswd=False):
    return _SerializeToUnicode(val, info=info, version=version, nsMap=nsMap, hidepasswd=hidepasswd).encode(XML_ENCODING)


## Serialize an object to unicode
#
# This function assumes CheckField(info, val) was already called
# @param val the value to serialize
# @param info the field
# @param version the version
# @param nsMap a dict of xml ns -> prefix
# @return the serialized object as unicode
def SerializeToUnicode(val, info=None, version=None, nsMap=None):
    return _SerializeToUnicode(val, info=info, version=version, nsMap=nsMap)


## Serialize an object to unicode
#
# This function assumes CheckField(info, val) was already called
# @param val the value to serialize
# @param info the field
# @param version the version
# @param nsMap a dict of xml ns -> prefix
# @return the serialized object as unicode
def _SerializeToUnicode(val, info=None, version=None, nsMap=None, hidepasswd=False):
    if hidepasswd and isinstance(val, DataObject) and val._wsdlName == "PasswordField":
        val.value = "(notShown)"
    if version is None:
        try:
            if isinstance(val, list):
                itemType = val.Item
                version = itemType._version
            else:
                if val is None:
                    # neither val nor version is given
                    return ""
                # Pick up the version from val
                version = val._version
        except AttributeError:
            version = BASE_VERSION
    if info is None:
        info = Object(name="obj", type=object, version=version, flags=0)

    writer = StringIO()
    SoapSerializer(writer, version, nsMap).Serialize(val, info)
    return writer.getvalue()


## Serialize fault detail
#
# Serializes a fault as the content of the detail element in a
# soapenv:Fault (i.e. without a LocalizedMethodFault wrapper).
#
# This function assumes CheckField(info, val) was already called
# @param val the value to serialize
# @param info the field
# @param version the version
# @param nsMap a dict of xml ns -> prefix
# @return the serialized object as a unicode string
def SerializeFaultDetail(val, info=None, version=None, nsMap=None, encoding=None):
    if version is None:
        try:
            if not isinstance(val, MethodFault):
                raise TypeError("%s is not a MethodFault" % str(val))
            version = val._version
        except AttributeError:
            version = BASE_VERSION
    if info is None:
        info = Object(name="obj", type=object, version=version, flags=0)

    writer = StringIO()
    SoapSerializer(writer, version, nsMap, encoding).SerializeFaultDetail(val, info)
    return writer.getvalue()


## SOAP serializer
#
class SoapSerializer:
    """SoapSerializer"""

    ## Serializer constructor
    #
    # @param writer File writer
    # @param version the version
    # @param nsMap a dict of xml ns -> prefix
    # @param encoding Deprecated this is not used during serialization since we always
    #        use utf-8 to encode a request message. We didn't remove the
    #        parameter so it is still compatible with clients that are still using it.
    def __init__(self, writer, version, nsMap, encoding=None):
        """Constructor"""
        self.writer = writer
        self.version = version
        self.nsMap = nsMap and nsMap or {}
        for ns, prefix in six.iteritems(self.nsMap):
            if prefix == "":
                self.defaultNS = ns
                break
        else:
            self.defaultNS = ""

        # Additional attr for outermost tag
        self.outermostAttrs = ""

        if version:
            self.outermostAttrs += ' versionId="%s"' % versionIdMap[version]

        # Fill in required xmlns, if not defined
        for nsPrefix, ns, attrName in [
            ("xsi", XMLNS_XSI, "xsiPrefix"),
            ("xsd", XMLNS_XSD, "xsdPrefix"),
        ]:
            prefix = self.nsMap.get(ns)
            if not prefix:
                prefix = nsPrefix
                self.outermostAttrs += ' xmlns:%s="%s"' % (prefix, ns)
                self.nsMap = self.nsMap.copy()
                self.nsMap[ns] = prefix
            setattr(self, attrName, prefix + ":")

    ## Serialize an object
    #
    # This function assumes CheckField(info, val) was already called
    # @param val the value to serialize
    # @param info the field
    def Serialize(self, val, info):
        """Serialize an object"""
        self._Serialize(val, info, self.defaultNS)

    ## Serialize fault detail
    #
    # Serializes a fault as the content of the detail element in a
    # soapenv:Fault (i.e. without a LocalizedMethodFault wrapper).
    #
    # This function assumes CheckField(info, val) was already called
    # @param val the value to serialize
    # @param info the field
    def SerializeFaultDetail(self, val, info):
        """Serialize an object"""
        self._SerializeDataObject(val, info, "", self.defaultNS)

    def _NSPrefix(self, ns):
        """Get xml ns prefix. self.nsMap must be set"""
        if ns == self.defaultNS:
            return ""
        prefix = self.nsMap[ns]
        return prefix and prefix + ":" or ""

    def _QName(self, typ, defNS):
        """Get fully qualified wsdl name (prefix:name)"""
        attr = ""
        ns, name = GetQualifiedWsdlName(typ)
        if ns == defNS:
            prefix = ""
        else:
            try:
                prefix = self.nsMap[ns]
            except KeyError:
                # We have not seen this ns before
                prefix = ns.split(":", 1)[-1]
                attr = ' xmlns:%s="%s"' % (prefix, ns)
        return attr, prefix and prefix + ":" + name or name

    ## Serialize an object to unicode (internal)
    #
    # @param val the value to serialize
    # @param info the field
    # @param defNS the default namespace
    def _Serialize(self, val, info, defNS):
        """Serialize an object"""
        if not IsChildVersion(self.version, info.version):
            return

        if val is None:
            if info.flags & F_OPTIONAL:
                return
            else:
                raise TypeError('Field "%s" is not optional' % info.name)
        elif isinstance(val, list) and len(val) == 0:
            if info.type is object:
                # Make sure an empty array assigned to Any is typed
                if not isinstance(val, Array):
                    raise TypeError('Field "%s": Cannot assign empty native python array to an Any' % info.name)
            elif info.flags & F_OPTIONAL:
                # Skip optional non-Any
                return
            else:
                raise TypeError('Field "%s" is not optional' % info.name)

        if self.outermostAttrs:
            attr = self.outermostAttrs
            self.outermostAttrs = None
        else:
            attr = ""
        currDefNS = defNS
        # Emit default ns if tag ns is not the same
        currTagNS = GetWsdlNamespace(info.version)
        if currTagNS != defNS:
            attr += ' xmlns="%s"' % currTagNS
            currDefNS = currTagNS

        if isinstance(val, DataObject):
            if isinstance(val, MethodFault):
                newVal = LocalizedMethodFault(fault=val, localizedMessage=val.msg)
                if info.type is object:
                    faultType = object
                else:
                    faultType = LocalizedMethodFault
                newInfo = Object(
                    name=info.name,
                    type=faultType,
                    version=info.version,
                    flags=info.flags,
                )
                self._SerializeDataObject(newVal, newInfo, attr, currDefNS)
            else:
                self._SerializeDataObject(val, info, attr, currDefNS)
        elif isinstance(val, ManagedObject):
            if info.type is object:
                nsattr, qName = self._QName(ManagedObject, currDefNS)
                attr += '%s %stype="%s"' % (nsattr, self.xsiPrefix, qName)
            if val._serverGuid is not None:
                attr += ' serverGuid="%s"' % (val._serverGuid)
            # val in vim type attr is not namespace qualified
            # TODO: Add a new "typens" attr?
            ns, name = GetQualifiedWsdlName(Type(val))
            attr += ' type="%s"' % (name)
            self.writer.write("<%s%s>%s</%s>" % (info.name, attr, val._moId, info.name))
        elif isinstance(val, list):
            if info.type is object:
                itemType = val.Item
                if itemType is ManagedMethod or itemType is PropertyPath or itemType is type:
                    tag = "string"
                    typ = GetVmodlType("string[]")
                elif issubclass(itemType, ManagedObject):
                    tag = "ManagedObjectReference"
                    typ = ManagedObject.Array
                else:
                    tag = GetWsdlName(itemType)
                    typ = Type(val)
                nsattr, qName = self._QName(typ, currDefNS)

                # For WSDL, since we set tag of ManagedObjects to ManagedObjectReferences,
                # the name of its array should be ArrayOfManagedObjectReference
                if qName.endswith("ArrayOfManagedObject"):
                    qName += "Reference"

                attr += '%s %stype="%s"' % (nsattr, self.xsiPrefix, qName)
                self.writer.write("<%s%s>" % (info.name, attr))

                itemInfo = Object(name=tag, type=itemType, version=info.version, flags=info.flags)
                for it in val:
                    self._Serialize(it, itemInfo, currDefNS)
                self.writer.write("</%s>" % info.name)
            else:
                itemType = info.type.Item
                itemInfo = Object(
                    name=info.name,
                    type=itemType,
                    version=info.version,
                    flags=info.flags,
                )
                for it in val:
                    self._Serialize(it, itemInfo, defNS)
        elif isinstance(val, type) or isinstance(val, type(Exception)):
            if info.type is object:
                attr += ' %stype="%sstring"' % (self.xsiPrefix, self.xsdPrefix)
            self.writer.write("<%s%s>%s</%s>" % (info.name, attr, GetWsdlName(val), info.name))
        elif isinstance(val, ManagedMethod):
            if info.type is object:
                attr += ' %stype="%sstring"' % (self.xsiPrefix, self.xsdPrefix)
            self.writer.write("<%s%s>%s</%s>" % (info.name, attr, val.info.wsdlName, info.name))
        elif isinstance(val, datetime):
            if info.type is object:
                nsattr, qName = self._QName(Type(val), currDefNS)
                attr += '%s %stype="%s"' % (nsattr, self.xsiPrefix, qName)
            result = Iso8601.ISO8601Format(val)
            self.writer.write("<%s%s>%s</%s>" % (info.name, attr, result, info.name))
        elif isinstance(val, binary):
            if info.type is object:
                nsattr, qName = self._QName(Type(val), currDefNS)
                attr += '%s %stype="%s"' % (nsattr, self.xsiPrefix, qName)
            result = base64.b64encode(val)
            if PY3:
                # In python3 the bytes result after the base64 encoding has a
                # leading 'b' which causes error when we use it to construct the
                # soap message. Workaround the issue by converting the result to
                # string. Since the result of base64 encoding contains only subset
                # of ASCII chars, converting to string will not change the value.
                result = str(result, XML_ENCODING)
            self.writer.write("<%s%s>%s</%s>" % (info.name, attr, result, info.name))
        elif isinstance(val, bool):
            if info.type is object:
                nsattr, qName = self._QName(Type(val), currDefNS)
                attr += '%s %stype="%s"' % (nsattr, self.xsiPrefix, qName)
            result = val and "true" or "false"
            self.writer.write("<%s%s>%s</%s>" % (info.name, attr, result, info.name))
        elif isinstance(val, six.integer_types) or isinstance(val, float):
            if info.type is object:
                nsattr, qName = self._QName(Type(val), currDefNS)
                attr += '%s %stype="%s"' % (nsattr, self.xsiPrefix, qName)
            result = six.text_type(val)
            self.writer.write("<%s%s>%s</%s>" % (info.name, attr, result, info.name))
        elif isinstance(val, Enum):
            if info.type is object:
                nsattr, qName = self._QName(Type(val), currDefNS)
                attr += '%s %stype="%s"' % (nsattr, self.xsiPrefix, qName)
            self.writer.write("<%s%s>%s</%s>" % (info.name, attr, val, info.name))
        else:
            if info.type is object:
                if isinstance(val, PropertyPath):
                    attr += ' %stype="%sstring"' % (self.xsiPrefix, self.xsdPrefix)
                else:
                    nsattr, qName = self._QName(Type(val), currDefNS)
                    attr += '%s %stype="%s"' % (nsattr, self.xsiPrefix, qName)

            if isinstance(val, six.binary_type):
                # Use UTF-8 rather than self.encoding.  self.encoding is for
                # output of serializer, while 'val' is our input.  And regardless
                # of what our output is, our input should be always UTF-8.  Yes,
                # it means that if you emit output in other encoding than UTF-8,
                # you cannot serialize it again once more.  That's feature, not
                # a bug.
                val = val.decode("UTF-8")
            result = XmlEscape(val)
            self.writer.write("<%s%s>%s</%s>" % (info.name, attr, result, info.name))

    ## Serialize a a data object (internal)
    #
    # @param val the value to serialize
    # @param info the field
    # @param attr attributes to serialized in the outermost elementt
    # @param currDefNS the current default namespace
    def _SerializeDataObject(self, val, info, attr, currDefNS):
        if info.flags & F_LINK:
            # Attribute is a link and Object is present instead of its key.
            # We need to serialize just the key and not the entire object
            self._Serialize(val.key, info, currDefNS)
            return
        dynType = GetCompatibleType(Type(val), self.version)
        if dynType != info.type:
            nsattr, qName = self._QName(dynType, currDefNS)
            attr += '%s %stype="%s"' % (nsattr, self.xsiPrefix, qName)
        self.writer.write("<%s%s>" % (info.name, attr))
        if dynType is LocalizedMethodFault:
            # Serialize a MethodFault as LocalizedMethodFault on wire
            # See PR 670229
            for prop in val._GetPropertyList():
                propVal = getattr(val, prop.name)
                if prop.name == "fault":
                    propVal = copy.copy(propVal)
                    propVal.msg = None
                    self._SerializeDataObject(propVal, prop, "", currDefNS)
                else:
                    self._Serialize(propVal, prop, currDefNS)
        else:
            for prop in val._GetPropertyList():
                self._Serialize(getattr(val, prop.name), prop, currDefNS)

        self.writer.write("</%s>" % info.name)


## Deserialize an object from a file or string
#
# This function will deserialize one top-level XML node.
# @param data the data to deserialize (a file object or string)
# @param resultType expected result type
# @param stub stub for moRef deserialization
# @return the deserialized object
def Deserialize(data, resultType=object, stub=None):
    parser = ParserCreate(namespace_separator=NS_SEP)
    ds = SoapDeserializer(stub)
    ds.Deserialize(parser, resultType)
    # Many existing tests pass in str directly in python2 for testing purpose.
    # But in python3 the input become unicode and the handling will fall into ParseFile case.
    # Adding unicode input support to make it more test friendly.
    if isinstance(data, six.binary_type) or isinstance(data, six.text_type):
        parser.Parse(data)
    else:
        parser.ParseFile(data)
    return ds.GetResult()


## Expat deserializer namespace handler
class ExpatDeserializerNSHandlers:
    def __init__(self, nsMap=None):
        # nsMap is a dict of ns prefix to a stack (list) of namespaces
        # The last element of the stack is current namespace
        if not nsMap:
            nsMap = {}
        self.nsMap = nsMap

    ## Get current default ns
    def GetCurrDefNS(self):
        return self._GetNamespaceFromPrefix()

    ## Get namespace and wsdl name from tag
    def GetNSAndWsdlname(self, tag):
        """Map prefix:name tag into ns, name"""
        idx = tag.find(":")
        if idx >= 0:
            prefix, name = tag[:idx], tag[idx + 1 :]
        else:
            prefix, name = None, tag
        # Map prefix to ns
        ns = self._GetNamespaceFromPrefix(prefix)
        return ns, name

    def _GetNamespaceFromPrefix(self, prefix=None):
        namespaces = self.nsMap.get(prefix)
        if namespaces:
            ns = namespaces[-1]
        else:
            ns = ""
        return ns

    ## Handle namespace begin
    def StartNamespaceDeclHandler(self, prefix, uri):
        namespaces = self.nsMap.get(prefix)
        if namespaces:
            namespaces.append(uri)
        else:
            self.nsMap[prefix] = [uri]

    ## Handle namespace end
    def EndNamespaceDeclHandler(self, prefix):
        self.nsMap[prefix].pop()


## SOAP -> Python Deserializer
class SoapDeserializer(ExpatDeserializerNSHandlers):
    ## Constructor
    #
    # @param self self
    # @param stub Stub adapter to use for deserializing moRefs
    def __init__(self, stub=None, version=None):
        ExpatDeserializerNSHandlers.__init__(self)
        self.stub = stub
        if version:
            self.version = version
        elif self.stub:
            self.version = self.stub.version
        else:
            self.version = None
        self.result = None

    ## Deserialize a SOAP object
    #
    # @param self self
    # @param parser an expat parser
    # @param resultType the static type of the result
    # @param isFault true if the response is a fault response
    # @param nsMap a dict of prefix -> [xml ns stack]
    # @return the deserialized object
    def Deserialize(self, parser, resultType=object, isFault=False, nsMap=None):
        self.isFault = isFault
        self.parser = parser
        self.origHandlers = GetHandlers(parser)
        SetHandlers(parser, GetHandlers(self))
        self.resultType = resultType
        self.stack = []
        self.data = ""
        self.serverGuid = None
        if issubclass(resultType, list):
            self.result = resultType()
        else:
            self.result = None
        if not nsMap:
            nsMap = {}
        self.nsMap = nsMap

    ## Get the result of deserialization
    #  The links will not be resolved. User needs to explicitly resolve them
    #  using LinkResolver.
    def GetResult(self):
        return self.result

    def SplitTag(self, tag):
        """Split tag into ns, name"""
        idx = tag.find(NS_SEP)
        if idx >= 0:
            return tag[:idx], tag[idx + 1 :]
        else:
            return "", tag

    def LookupWsdlType(self, ns, name, allowManagedObjectReference=False):
        """Lookup wsdl type. Handle special case for some vmodl version"""
        try:
            return GetWsdlType(ns, name)
        except KeyError:
            if allowManagedObjectReference:
                if name.endswith("ManagedObjectReference") and ns == XMLNS_VMODL_BASE:
                    return GetWsdlType(ns, name[: -len("Reference")])
            # WARNING!!! This is a temporary hack to get around server not
            # honoring @service tag (see bug 521744). Once it is fix, I am
            # going to back out this change
            if name.endswith("ManagedObjectReference") and allowManagedObjectReference:
                return GetWsdlType(XMLNS_VMODL_BASE, name[: -len("Reference")])
            return GuessWsdlType(name)

    ## Handle an opening XML tag
    def StartElementHandler(self, tag, attr):
        self.data = ""
        self.serverGuid = None
        deserializeAsLocalizedMethodFault = True
        if not self.stack:
            if self.isFault:
                ns, name = self.SplitTag(tag)
                objType = self.LookupWsdlType(ns, name[:-5])
                # Only top level soap fault should be deserialized as method fault
                deserializeAsLocalizedMethodFault = False
            else:
                objType = self.resultType
        elif isinstance(self.stack[-1], list):
            objType = self.stack[-1].Item
        elif isinstance(self.stack[-1], DataObject):
            # TODO: Check ns matches DataObject's namespace
            ns, name = self.SplitTag(tag)
            objType = self.stack[-1]._GetPropertyInfo(name).type

            # LocalizedMethodFault <fault> tag should be deserialized as method fault
            if name == "fault" and isinstance(self.stack[-1], LocalizedMethodFault):
                deserializeAsLocalizedMethodFault = False
        else:
            raise TypeError("Invalid type for tag %s" % tag)

        xsiType = attr.get(XSI_TYPE)
        if xsiType:
            # Ignore dynamic type for TypeName, MethodName, PropertyPath
            # @bug 150459
            if not (objType is type or objType is ManagedMethod or objType is PropertyPath):
                ns, name = self.GetNSAndWsdlname(xsiType)
                dynType = self.LookupWsdlType(ns, name, allowManagedObjectReference=True)
                # TODO: Should be something like...
                #   dynType must be narrower than objType, except for
                #   ManagedObjectReference
                if not (issubclass(dynType, list) and issubclass(objType, list)):
                    objType = dynType
        else:
            if issubclass(objType, list):
                objType = objType.Item

        if self.version:
            objType = GetCompatibleType(objType, self.version)
        if issubclass(objType, ManagedObject):
            typeAttr = attr["type"]
            # val in vim type attr is not namespace qualified
            # However, this doesn't hurt to strip out namespace
            # TODO: Get the ns from "typens" attr?
            ns, name = self.GetNSAndWsdlname(typeAttr)

            if "serverGuid" in attr:
                if not self.stub or not self.stub.SupportServerGUIDs():
                    self.serverGuid = attr["serverGuid"]
            self.stack.append(self.LookupWsdlType(ns, name))
        elif issubclass(objType, DataObject) or issubclass(objType, list):
            if deserializeAsLocalizedMethodFault and issubclass(objType, Exception):
                objType = LocalizedMethodFault
            self.stack.append(objType())
        else:
            self.stack.append(objType)

    ## Handle a closing XML tag
    def EndElementHandler(self, tag):
        try:
            obj = self.stack.pop()
        except IndexError:
            SetHandlers(self.parser, self.origHandlers)
            handler = self.parser.EndElementHandler
            del self.parser, self.origHandlers, self.stack, self.resultType
            if handler:
                return handler(tag)
            return

        data = self.data
        if isinstance(obj, type) or isinstance(obj, type(Exception)):
            if obj is type:
                if data is None or data == "":
                    obj = None
                else:
                    try:
                        # val in type val is not namespace qualified
                        # However, this doesn't hurt to strip out namespace
                        ns, name = self.GetNSAndWsdlname(data)
                        obj = self.LookupWsdlType(ns, name)
                    except KeyError:
                        raise TypeError(data)
            elif obj is ManagedMethod:
                # val in Method val is not namespace qualified
                # However, this doesn't hurt to strip out namespace
                ns, name = self.GetNSAndWsdlname(data)
                try:
                    obj = GetWsdlMethod(ns, name)
                except KeyError:
                    obj = GuessWsdlMethod(name)
            elif obj is bool:
                if data == "0" or data.lower() == "false":
                    obj = bool(False)
                elif data == "1" or data.lower() == "true":
                    obj = bool(True)
                else:
                    raise TypeError(data)
            elif obj is binary:
                # Raise type error if decode failed
                obj = obj(base64.b64decode(data))
            elif obj is str:
                try:
                    obj = str(data)
                except UnicodeError:
                    obj = data
            elif obj is datetime:
                obj = Iso8601.ParseISO8601(data)
                if not obj:
                    raise TypeError(data)
            # issubclass is very expensive. Test last
            elif issubclass(obj, ManagedObject):
                obj = obj(data, self.stub, self.serverGuid)
            elif issubclass(obj, Enum):
                obj = getattr(obj, data)
            else:
                obj = obj(data)
        elif isinstance(obj, LocalizedMethodFault):
            obj.fault.msg = obj.localizedMessage
            obj = obj.fault

        if self.stack:
            top = self.stack[-1]
            if isinstance(top, list):
                top.append(obj)
            elif isinstance(top, DataObject):
                ns, name = self.SplitTag(tag)
                info = top._GetPropertyInfo(name)

                if not isinstance(obj, list) and issubclass(info.type, list):
                    getattr(top, info.name).append(obj)
                else:
                    setattr(top, info.name, obj)
            else:
                ns, name = self.SplitTag(tag)
                setattr(top, name, obj)
        else:
            if not isinstance(obj, list) and issubclass(self.resultType, list):
                self.result.append(obj)
            else:
                self.result = obj
                SetHandlers(self.parser, self.origHandlers)
                del self.parser, self.origHandlers, self.stack, self.resultType

    ## Handle text data
    def CharacterDataHandler(self, data):
        self.data += data


## SOAP Response Deserializer class
class SoapResponseDeserializer(ExpatDeserializerNSHandlers):
    ## Constructor
    #
    # @param self self
    # @param stub Stub adapter to use for deserializing moRefs
    def __init__(self, stub):
        ExpatDeserializerNSHandlers.__init__(self)
        self.stub = stub
        self.deser = SoapDeserializer(stub)
        self.soapFaultTag = XMLNS_SOAPENV + NS_SEP + "Fault"

    ## Deserialize a SOAP response
    #
    # @param self self
    # @param response the response (a file object or a string)
    # @param resultType expected result type
    # @param nsMap a dict of prefix -> [xml ns stack]
    # @return the deserialized object
    def Deserialize(self, response, resultType, nsMap=None):
        self.resultType = resultType
        self.stack = []
        self.msg = ""
        self.deser.result = None
        self.isFault = False
        self.parser = ParserCreate(namespace_separator=NS_SEP)
        try:  # buffer_text only in python >= 2.3
            self.parser.buffer_text = True
        except AttributeError:
            pass
        if not nsMap:
            nsMap = {}
        self.nsMap = nsMap
        SetHandlers(self.parser, GetHandlers(self))
        # Many existing tests pass in str directly in python2 for testing purpose.
        # But in python3 the input become unicode and the handling will fall into ParseFile case.
        # Adding unicode input support to make it more test friendly.
        if isinstance(response, six.binary_type) or isinstance(response, six.text_type):
            self.parser.Parse(response)
        else:
            self.parser.ParseFile(response)
        result = self.deser.GetResult()
        if self.isFault:
            if result is None:
                result = GetVmodlType("vmodl.RuntimeFault")()
            result.msg = self.msg
        del self.resultType, self.stack, self.parser, self.msg, self.data, self.nsMap
        return result

    ## Handle an opening XML tag
    def StartElementHandler(self, tag, attr):
        self.data = ""
        if tag == self.soapFaultTag:
            self.isFault = True
        elif self.isFault and tag == "detail":
            self.deser.Deserialize(self.parser, object, True, self.nsMap)
        elif tag.endswith("Response"):
            self.deser.Deserialize(self.parser, self.resultType, False, self.nsMap)

    ## Handle text data
    def CharacterDataHandler(self, data):
        self.data += data

    ## Handle a closing XML tag
    def EndElementHandler(self, tag):
        if self.isFault and tag == "faultstring":
            try:
                self.msg = str(self.data)
            except UnicodeError:
                self.msg = self.data


## Base class that implements common functionality for stub adapters.
## Method that must be provided by the implementation class:
## -- InvokeMethod(ManagedObject mo, Object methodInfo, Object[] args)
class StubAdapterBase(StubAdapterAccessorMixin):
    def __init__(self, version):
        StubAdapterAccessorMixin.__init__(self)
        self.ComputeVersionInfo(version)

    ## Compute the version information for the specified namespace
    #
    # @param ns the namespace
    def ComputeVersionInfo(self, version):
        # Make sure we do NOT fallback to an older version
        if hasattr(self, "version") and IsChildVersion(self.version, version):
            # print("WARNING: stub degrading: " + self.version + " -> " + version)
            return

        versionNS = GetVersionNamespace(version)
        if versionNS.find("/") >= 0:
            self.versionId = '"urn:%s"' % versionNS
        else:
            self.versionId = ""
        self.version = version


## Base class that implements common functionality for SOAP-based stub adapters.
## Method that must be provided by the implementation class:
## -- InvokeMethod(ManagedObject mo, Object methodInfo, Object[] args)
class SoapStubAdapterBase(StubAdapterBase):
    ## Serialize a VMOMI request to SOAP
    #
    # @param version API version
    # @param mo the 'this'
    # @param info method info
    # @param args method arguments
    # @return the serialized request
    def SerializeRequest(self, mo, info, args):
        if not IsChildVersion(self.version, info.version):
            raise GetVmodlType("vmodl.fault.MethodNotFound")(receiver=mo, method=info.name)
        nsMap = SOAP_NSMAP.copy()
        defaultNS = GetWsdlNamespace(self.version)
        nsMap[defaultNS] = ""

        # Add xml header and soap envelope
        result = [XML_HEADER, "\n", SOAP_ENVELOPE_START]
        # Add request context and samlToken to soap header, if exists
        reqContexts = copy.deepcopy(GetRequestContext())
        samlToken = getattr(self, "samlToken", None)

        if reqContexts or samlToken:
            result.append(SOAP_HEADER_START)
            for key, val in six.iteritems(reqContexts):
                # Note: Support req context of string type only
                if not isinstance(val, six.string_types):
                    raise TypeError("Request context key (%s) has non-string value (%s) of %s" % (key, val, type(val)))
                ret = _SerializeToUnicode(
                    val,
                    Object(name=key, type=str, version=self.version),
                    self.version,
                    nsMap,
                )
                result.append(ret)
            if samlToken:
                result.append("%s %s %s" % (WSSE_HEADER_START, samlToken, WSSE_HEADER_END))
            result.append(SOAP_HEADER_END)
            result.append("\n")

        # Serialize soap body
        result.extend(
            [
                SOAP_BODY_START,
                '<%s xmlns="%s">' % (info.wsdlName, defaultNS),
                _SerializeToUnicode(
                    mo,
                    Object(name="_this", type=ManagedObject, version=self.version),
                    self.version,
                    nsMap,
                ),
            ]
        )

        # Serialize soap request parameters
        for param, arg in zip(info.params, args):
            result.append(_SerializeToUnicode(arg, param, self.version, nsMap))
        result.extend(["</%s>" % info.wsdlName, SOAP_BODY_END, SOAP_ENVELOPE_END])
        return "".join(result).encode(XML_ENCODING)


## Subclass of HTTPConnection that connects over a Unix domain socket
## instead of a TCP port.  The path of the socket is passed in place of
## the hostname.  Fairly gross but does the job.
class UnixSocketConnection(six.moves.http_client.HTTPConnection):
    # The HTTPConnection ctor expects a single argument, which it interprets
    # as the host to connect to; for UnixSocketConnection, we instead interpret
    # the parameter as the filesystem path of the Unix domain socket.
    def __init__(self, path):
        # Pass '' as the host to HTTPConnection; it doesn't really matter
        # what we pass (since we've overridden the connect method) as long
        # as it's a valid string.
        six.moves.http_client.HTTPConnection.__init__(self, "")
        self.path = path

    def connect(self):
        # Hijack the connect method of HTTPConnection to connect to the
        # specified Unix domain socket instead.  Obey the same contract
        # as HTTPConnection.connect, which puts the socket in self.sock.
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(self.path)
        self.sock = sock


try:
    # The ssl module is not available in python versions less than 2.6
    SSL_THUMBPRINTS_SUPPORTED = True

    import ssl
    import hashlib

    def _VerifyThumbprint(thumbprint, connection):
        """If there is a thumbprint, connect to the server and verify that the
        SSL certificate matches the given thumbprint.  An exception is thrown
        if there is a mismatch."""
        if thumbprint and isinstance(connection, six.moves.http_client.HTTPSConnection):
            if not connection.sock:
                connection.connect()
            derCert = connection.sock.getpeercert(True)
            thumbprint_len = len(thumbprint)
            if thumbprint_len == 40:
                sha = hashlib.sha1()  # nosec
            elif thumbprint_len == 64:
                sha = hashlib.sha256()
            elif thumbprint_len == 128:
                sha = hashlib.sha512()
            else:
                raise Exception("SHA thumbprint LENGTH is not valid -- %s" % thumbprint)
            sha.update(derCert)
            shaDigest = sha.hexdigest().lower()
            if shaDigest != thumbprint:
                raise ThumbprintMismatchException(thumbprint, shaDigest)

    # Function used to wrap sockets with SSL
    _SocketWrapper = ssl.wrap_socket

except ImportError:
    SSL_THUMBPRINTS_SUPPORTED = False

    def _VerifyThumbprint(thumbprint, connection):
        if thumbprint and isinstance(connection, six.moves.http_client.HTTPSConnection):
            raise Exception("Thumbprint verification not supported on python < 2.6")

    def _SocketWrapper(rawSocket, keyfile, certfile, *args, **kwargs):
        wrappedSocket = socket.ssl(rawSocket, keyfile, certfile)
        return six.moves.http_client.FakeSocket(rawSocket, wrappedSocket)


## Internal version of http connection
class _HTTPConnection(six.moves.http_client.HTTPConnection):
    def __init__(self, *args, **kwargs):
        # Only pass in the named arguments that HTTPConnection constructor
        # understands
        tmpKwargs = {}
        for key in six.moves.http_client.HTTPConnection.__init__.__code__.co_varnames:
            if key in kwargs and key != "self":
                tmpKwargs[key] = kwargs[key]
        six.moves.http_client.HTTPConnection.__init__(self, *args, **tmpKwargs)


## Internal version of https connection
#
# Support ssl.wrap_socket params which are missing from httplib
# HTTPSConnection (e.g. ca_certs)
# Note: Only works iff the ssl params are passing in as kwargs
class _HTTPSConnection(six.moves.http_client.HTTPSConnection):
    def __init__(self, *args, **kwargs):
        # Extract ssl.wrap_socket param unknown to httplib.HTTPSConnection,
        # and push back the params in connect()
        self._sslArgs = {}
        tmpKwargs = kwargs.copy()
        for key in [
            "server_side",
            "cert_reqs",
            "ssl_version",
            "ca_certs",
            "do_handshake_on_connect",
            "suppress_ragged_eofs",
            "ciphers",
        ]:
            if key in tmpKwargs:
                self._sslArgs[key] = tmpKwargs.pop(key)
        six.moves.http_client.HTTPSConnection.__init__(self, *args, **tmpKwargs)

    ## Override connect to allow us to pass in additional ssl paramters to
    #  ssl.wrap_socket (e.g. cert_reqs, ca_certs for ca cert verification)
    def connect(self):
        if len(self._sslArgs) == 0:
            # No override
            six.moves.http_client.HTTPSConnection.connect(self)
            return

        # Big hack. We have to copy and paste the httplib connect fn for
        # each python version in order to handle extra ssl paramters. Yuk!
        if hasattr(self, "source_address"):
            # Python 2.7
            sock = socket.create_connection((self.host, self.port), self.timeout, self.source_address)
            if self._tunnel_host:
                self.sock = sock
                self._tunnel()
            self.sock = ssl.wrap_socket(sock, self.key_file, self.cert_file, **self._sslArgs)  # nosec
        elif hasattr(self, "timeout"):
            # Python 2.6
            sock = socket.create_connection((self.host, self.port), self.timeout)
            self.sock = ssl.wrap_socket(sock, self.key_file, self.cert_file, **self._sslArgs)  # nosec
        else:
            # Unknown python version. Do nothing
            six.moves.http_client.HTTPSConnection.connect(self)
            return

        # TODO: Additional verification of peer cert if needed
        # cert_reqs = self._sslArgs.get("cert_reqs", ssl.CERT_NONE)
        # ca_certs = self._sslArgs.get("ca_certs", None)
        # if cert_reqs != ssl.CERT_NONE and ca_certs:
        #   if hasattr(self.sock, "getpeercert"):
        #      # TODO: verify peer cert
        #      dercert = self.sock.getpeercert(False)
        #      # pemcert = ssl.DER_cert_to_PEM_cert(dercert)


## Stand-in for the HTTPSConnection class that will connect to a proxy and
## issue a CONNECT command to start an SSL tunnel.
class SSLTunnelConnection(object):
    # @param proxyPath The path to pass to the CONNECT command.
    def __init__(self, proxyPath):
        self.proxyPath = proxyPath

    # Connects to a proxy server and initiates a tunnel to the destination
    # specified by proxyPath.  If successful, a new HTTPSConnection is returned.
    # For Python Version < 2.7.9. cert_reqs=CERT_OPTIONAL to verify server certificate
    #
    # @param path The destination URL path.
    # @param key_file **** Deprecated. Please pass context instread ****
    #                     sslContext.load_cert_chain(cert_file, key_file)
    #                     The SSL key file to use when wrapping the socket.
    # @param cert_file **** Deprecated. Please pass context instread ****
    #                     sslContext.load_cert_chain(cert_file, key_file)
    #                     The SSL certificate file to use when wrapping the socket.
    # @param context SSL Context describing the various SSL options. It is only
    #                   supported in Python 2.7.9 or higher.
    #                   if context is used, load cert & key to the context with API
    #                   context = ssl.create_default_context(cafile=ca_cert_file)
    #                   context.load_cert_chain(key_file, cert_file)
    # @param kwargs In case caller passed in extra parameters not handled by
    #        SSLTunnelConnection
    def __call__(self, path, key_file=None, cert_file=None, context=None, **kwargs):
        _sslArgs = {}
        tmpKwargs = kwargs.copy()
        for key in [
            "server_side",
            "cert_reqs",
            "ssl_version",
            "ca_certs",
            "do_handshake_on_connect",
            "suppress_ragged_eofs",
            "ciphers",
        ]:
            if key in tmpKwargs:
                _sslArgs[key] = tmpKwargs.pop(key)
        if context:
            tmpKwargs["context"] = context
            if cert_file and key_file:
                tmpKwargs["context"] = _CloneSSLContext(context, cert_file, key_file)
        else:
            if key_file:
                tmpKwargs["key_file"] = key_file
            if cert_file:
                tmpKwargs["cert_file"] = cert_file
        tunnel = _HTTPConnection(path, **kwargs)
        tunnel.request("CONNECT", self.proxyPath)
        resp = tunnel.getresponse()
        if resp.status != 200:
            raise six.moves.http_client.HTTPException("%d %s" % (resp.status, resp.reason))
        host, port = urllib.splitport(path)
        if not "port" in tmpKwargs:
            tmpKwargs["port"] = port
        retval = six.moves.http_client.HTTPSConnection(host=host, **tmpKwargs)
        if hasattr(retval, "_context"):
            if host in ["localhost", "127.0.0.1", "::1"]:
                retval._context.check_hostname = False
            if "ca_certs" in kwargs and kwargs["ca_certs"]:
                retval._context.load_verify_locations(kwargs["ca_certs"])
            # Call set_tunnel when proxyPath is a stand alone proxy host.
            if (
                _CheckIPv4(urllib.splitport(self.proxyPath)[0])
                or _CheckIPv6(urllib.splitport(self.proxyPath)[0])
                or _CheckHostname(urllib.splitport(self.proxyPath)[0])
            ):
                retval.set_tunnel(self.proxyPath)
            # Call wrap_socket if ProxyPath is VC inbuilt proxyPath ex: /sdkTunnel
            else:
                retval.sock = retval._context.wrap_socket(sock=tunnel.sock, server_hostname=host)
        else:
            if host in ["localhost", "127.0.0.1", "::1"]:
                _sslArgs["cert_reqs"] = ssl.CERT_NONE
            retval.sock = ssl.wrap_socket(tunnel.sock, keyfile=key_file, certfile=cert_file, **_sslArgs)  # nosec
        return retval


class GzipReader:
    GZIP = 1
    DEFLATE = 2

    def __init__(self, rfile, encoding=GZIP, readChunkSize=512):
        self.rfile = rfile
        self.chunks = []
        self.bufSize = 0  # Remaining buffer
        assert encoding in (GzipReader.GZIP, GzipReader.DEFLATE)  # nosec
        self.encoding = encoding
        self.unzip = None
        self.readChunkSize = readChunkSize

    def _CreateUnzip(self, firstChunk):
        import zlib

        if self.encoding == GzipReader.GZIP:
            wbits = zlib.MAX_WBITS + 16
        elif self.encoding == GzipReader.DEFLATE:
            # Sniff out real deflate format
            chunkLen = len(firstChunk)
            # Assume raw deflate
            wbits = -zlib.MAX_WBITS
            if firstChunk[:3] == ["\x1f", "\x8b", "\x08"]:
                # gzip: Apache mod_deflate will send gzip. Yurk!
                wbits = zlib.MAX_WBITS + 16
            elif chunkLen >= 2:
                b0 = ord(firstChunk[0])
                b1 = ord(firstChunk[1])
                if (b0 & 0xF) == 8 and (((b0 * 256 + b1)) % 31) == 0:
                    # zlib deflate
                    wbits = min(((b0 & 0xF0) >> 4) + 8, zlib.MAX_WBITS)
        else:
            assert False  # nosec
        self.unzip = zlib.decompressobj(wbits)
        return self.unzip

    def read(self, bytes=-1):
        chunks = self.chunks
        bufSize = self.bufSize

        while bufSize < bytes or bytes == -1:
            # Read and decompress
            chunk = self.rfile.read(self.readChunkSize)

            if self.unzip == None:
                self._CreateUnzip(chunk)

            if chunk:
                inflatedChunk = self.unzip.decompress(chunk)
                bufSize += len(inflatedChunk)
                chunks.append(inflatedChunk)
            else:
                # Returns whatever we have
                break

        if bufSize <= bytes or bytes == -1:
            leftoverBytes = 0
            leftoverChunks = []
        else:
            leftoverBytes = bufSize - bytes
            # Adjust last chunk to hold only the left over bytes
            lastChunk = chunks.pop()
            chunks.append(lastChunk[:-leftoverBytes])
            leftoverChunks = [lastChunk[-leftoverBytes:]]

        self.chunks = leftoverChunks
        self.bufSize = leftoverBytes

        buf = b"".join(chunks)
        return buf


## SOAP stub adapter object
class SoapStubAdapter(SoapStubAdapterBase):
    ## Constructor
    #
    # The endpoint can be specified individually as either a host/port
    # combination, or with a URL (using a url= keyword).
    # @param self self
    # @param host host
    # @param port port (pass negative port number for no SSL)
    # @param **** Deprecated. Please use version instead **** ns API namespace
    # @param path location of SOAP VMOMI service
    # @param url URL (overrides host, port, path if set)
    # @param sock unix domain socket path (overrides host, port, url if set)
    # @param poolSize size of HTTP connection pool
    # @param certKeyFile **** Deprecated. Please load cert to context and pass context instread ****
    #                       sslContext.load_cert_chain(key_file, cert_file)
    #                       The path to the PEM-encoded SSL private key file.
    # @param certFile **** Deprecated. Please pass context instread ****
    #                       sslContext.load_cert_chain(key_file, cert_file)
    #                       The path to the PEM-encoded SSL certificate file.
    # @param httpProxyHost The host name of the proxy server.
    # @param httpProxyPort The proxy server port.
    # @param sslProxyPath Path to use when tunneling through VC's reverse proxy.
    # @param thumbprint The SHA1/SHA256/SHA512 thumbprint of the server's SSL certificate.
    #   Some use a thumbprint of the form xx:xx:xx..:xx.  We ignore the ":"
    #   characters.  If set to None, any thumbprint is accepted.
    # @param cacertsFile **** Deprecated. Please load cert to context and pass context instread ****
    #                    sslContext.load_verify_locations(cafile=ca_cert_file)**
    #                    CA certificates file in PEM format
    # @param version API version
    # @param connectionPoolTimeout Timeout in secs for idle connections in client pool. Use -1 to disable any timeout.
    # @param samlToken SAML Token that should be used in SOAP security header for login
    # @param sslContext SSL Context describing the various SSL options. It is only
    #                   supported in Python 2.7.9 or higher.
    #                   if sslContext is used, load cert & key to the context with API
    #                   sslContext = ssl.create_default_context(cafile=ca_cert_file)
    #                   sslContext.load_cert_chain(key_file, cert_file)
    # @param httpConnectionTimeout Timeout in secs for http requests.
    def __init__(
        self,
        host="localhost",
        port=443,
        ns=None,
        path="/sdk",
        url=None,
        sock=None,
        poolSize=5,
        certFile=None,
        certKeyFile=None,
        httpProxyHost=None,
        httpProxyPort=80,
        sslProxyPath=None,
        thumbprint=None,
        cacertsFile=None,
        version=None,
        acceptCompressedResponses=True,
        connectionPoolTimeout=CONNECTION_POOL_IDLE_TIMEOUT_SEC,
        samlToken=None,
        sslContext=None,
        httpConnectionTimeout=None,
    ):
        if ns:
            assert version is None  # nosec
            version = versionMap[ns]
        elif not version:
            version = "vim.version.version9"
        SoapStubAdapterBase.__init__(self, version=version)
        self.cookie = ""
        if sock:
            self.scheme = UnixSocketConnection
            # Store sock in the host member variable because that's where
            # the UnixSocketConnection ctor expects to find it -- see above
            self.host = sock
        elif url:
            scheme, self.host, urlpath = urlparse(url)[:3]
            # Only use the URL path if it's sensible, otherwise use the path
            # keyword argument as passed in.
            if urlpath not in ("", "/"):
                path = urlpath
            self.scheme = scheme == "http" and _HTTPConnection or scheme == "https" and _HTTPSConnection
        else:
            port, self.scheme = port < 0 and (-port, _HTTPConnection) or (port, _HTTPSConnection)
            if host.find(":") != -1 and host[0] != "[":  # is IPv6?
                host = "[" + host + "]"
            self.host = "%s:%d" % (host, port)

        self.path = path
        if thumbprint:
            self.thumbprint = thumbprint.replace(":", "").lower()
            if len(self.thumbprint) not in (40, 64, 128):
                raise Exception("Invalid SHA thumbprint -- %s" % thumbprint)
        else:
            self.thumbprint = None

        self.is_ssl_tunnel = False
        if sslProxyPath:
            self.scheme = SSLTunnelConnection(sslProxyPath)
            self.is_ssl_tunnel = True
        elif httpProxyHost:
            if self.scheme == _HTTPSConnection:
                self.scheme = SSLTunnelConnection(self.host)
                self.is_ssl_tunnel = True
            else:
                if url:
                    self.path = url
                else:
                    self.path = "http://%s/%s" % (self.host, path)

            # Is httpProxyHost IPv6
            if httpProxyHost.find(":") != -1 and httpProxyHost[0] != "[":
                httpProxyHost = "[" + httpProxyHost + "]"

            # Swap the actual host with the proxy.
            self.host = "%s:%d" % (httpProxyHost, httpProxyPort)
        self.poolSize = poolSize
        self.pool = []
        self.connectionPoolTimeout = connectionPoolTimeout
        self.lock = six.moves._thread.allocate_lock()
        self.schemeArgs = {}
        if sslContext:
            self.schemeArgs["context"] = sslContext
            if certFile and certKeyFile:
                self.schemeArgs["context"] = _CloneSSLContext(sslContext, certFile, certKeyFile)
        else:
            if certKeyFile:
                self.schemeArgs["key_file"] = certKeyFile
            if certFile:
                self.schemeArgs["cert_file"] = certFile
        if cacertsFile:
            self.schemeArgs["ca_certs"] = cacertsFile
            self.schemeArgs["cert_reqs"] = ssl.CERT_REQUIRED
        if httpConnectionTimeout:
            self.schemeArgs["timeout"] = httpConnectionTimeout
        self.samlToken = samlToken
        self.requestModifierList = []
        self._acceptCompressedResponses = acceptCompressedResponses

    # Force a socket shutdown. Before python 2.7, ssl will fail to close
    # the socket (http://bugs.python.org/issue10127).
    # Not making this a part of the actual _HTTPSConnection since the internals
    # of the httplib.HTTP*Connection seem to pass around the descriptors and
    # depend on the behavior that close() still leaves the socket semi-functional.
    if sys.version_info[:2] < (2, 7):

        def _CloseConnection(self, conn):
            if self.scheme == _HTTPSConnection and conn.sock:
                conn.sock.shutdown(socket.SHUT_RDWR)
            conn.close()

    else:

        def _CloseConnection(self, conn):
            conn.close()

    # Context modifier used to modify the SOAP request.
    # @param func The func that takes in the serialized message and modifies the
    #   the request. The func is appended to the requestModifierList and then
    #   popped after the request is modified.
    @contextlib.contextmanager
    def requestModifier(self, func):
        self.requestModifierList.append(func)
        try:
            yield
        finally:
            self.requestModifierList.pop()

    ## Invoke a managed method
    #
    # @param self self
    # @param mo the 'this'
    # @param info method info
    # @param args arguments
    # @param outerStub If not-None, this should be a reference to the wrapping
    #   stub adapter.  Any ManagedObject references returned from this method
    #   will have outerStub in their _stub field.  Note that this also changes
    #   the return type to a tuple containing the HTTP status and the
    #   deserialized object so that it's easier to distinguish an API error from
    #   a connection error.
    def InvokeMethod(self, mo, info, args, outerStub=None):
        if outerStub is None:
            outerStub = self

        headers = {
            "Cookie": self.cookie,
            "SOAPAction": self.versionId,
            "Content-Type": "text/xml; charset=%s" % XML_ENCODING,
            "User-Agent": "pyvmomi Python/{0} ({1}; {2}; {3})".format(PYTHON_VERSION, OS_NAME, OS_VERSION, OS_ARCH),
        }
        if self._acceptCompressedResponses:
            headers["Accept-Encoding"] = "gzip, deflate"
        # The HTTPConnection.request() method internally extracts the hostname from
        # self.path. This implementation does not support hostname as IPv6
        # address as per RFC 2732, which involves wrapping the IPv6 address with
        # []. If the hostname is provided as part of 'headers', then the
        # HTTPConnection.request() does not extract it from self.path. Since
        # SoapStubAdapter.__init__() supports IPv6 Address in hostname the fix
        # is to add self.host to 'headers'
        # This issue is fixed in python >= 2.7 http://bugs.python.org/issue5111
        # Diff: http://bugs.python.org/file14425/5111.diff
        if sys.version_info[:2] < (2, 7) and self.host:
            headers["host"] = self.host
        req = self.SerializeRequest(mo, info, args)
        for modifier in self.requestModifierList:
            req = modifier(req)
        conn = self.GetConnection()
        try:
            conn.request("POST", self.path, req, headers)
            resp = conn.getresponse()
        except (socket.error, six.moves.http_client.HTTPException):
            # The server is probably sick, drop all of the cached connections.
            self.DropConnections()
            raise
        cookie = resp.getheader("set-cookie")
        status = resp.status

        if cookie:
            self.cookie = cookie
        if status == 200 or status == 500:
            try:
                fd = resp
                encoding = resp.getheader("Content-Encoding", "identity").lower()
                if encoding == "gzip":
                    fd = GzipReader(resp, encoding=GzipReader.GZIP)
                elif encoding == "deflate":
                    fd = GzipReader(resp, encoding=GzipReader.DEFLATE)
                obj = SoapResponseDeserializer(outerStub).Deserialize(fd, info.result)
            except:
                self._CloseConnection(conn)
                # The server might be sick, drop all of the cached connections.
                self.DropConnections()
                raise
            else:
                resp.read()
                self.ReturnConnection(conn)
            if outerStub != self:
                return (status, obj)
            if status == 200:
                return obj
            else:
                raise obj  # pylint: disable-msg=E0702
        else:
            self._CloseConnection(conn)
            raise six.moves.http_client.HTTPException("%d %s" % (resp.status, resp.reason))

    ## Clean up connection pool to throw away idle timed-out connections
    #  SoapStubAdapter lock must be acquired before this method is called.
    def _CloseIdleConnections(self):
        if self.connectionPoolTimeout >= 0:
            currentTime = time.time()
            idleConnections = []
            for conn, lastAccessTime in self.pool:
                idleTime = currentTime - lastAccessTime
                if idleTime >= self.connectionPoolTimeout:
                    i = self.pool.index((conn, lastAccessTime))
                    idleConnections = self.pool[i:]
                    self.pool = self.pool[:i]
                    break

            for conn, _ in idleConnections:
                self._CloseConnection(conn)

    ## Get a HTTP connection from the pool
    def GetConnection(self):
        self.lock.acquire()
        self._CloseIdleConnections()
        if self.pool:
            result, _ = self.pool.pop(0)
            self.lock.release()
        else:
            self.lock.release()
            result = self.scheme(self.host, **self.schemeArgs)

            # Always disable NAGLE algorithm
            #
            # Python httplib (2.6 and below) is splitting a http request into 2
            # packets (header and body). It first send the header, but will not
            # send the body until it receives the ack (for header) from server
            # [NAGLE at work]. The delayed ack time on ESX is around 40 - 100 ms
            # (depends on version) and can go up to 200 ms. This effectively slow
            # down each pyVmomi call by the same amount of time.
            #
            # Disable NAGLE on client will force both header and body packets to
            # get out immediately, and eliminated the delay
            #
            # This bug is fixed in python 2.7, however, only if the request
            # body is a string (which is true for now)
            if sys.version_info[:2] < (2, 7):
                self.DisableNagle(result)

            _VerifyThumbprint(self.thumbprint, result)

        return result

    ## Drop all cached connections to the server.
    def DropConnections(self):
        self.lock.acquire()
        oldConnections = self.pool
        self.pool = []
        self.lock.release()
        for conn, _ in oldConnections:
            self._CloseConnection(conn)

    ## Return a HTTP connection to the pool
    def ReturnConnection(self, conn):
        self.lock.acquire()
        self._CloseIdleConnections()
        # In case of ssl tunneling, only add the conn if the conn has not been closed
        if len(self.pool) < self.poolSize and (not self.is_ssl_tunnel or conn.sock):
            self.pool.insert(0, (conn, time.time()))
            self.lock.release()
        else:
            self.lock.release()
            self._CloseConnection(conn)

    ## Disable nagle on a http connections
    def DisableNagle(self, conn):
        # Override connections' connect function to force disable NAGLE
        if self.scheme != UnixSocketConnection and getattr(conn, "connect"):
            orgConnect = conn.connect

            def ConnectDisableNagle(*args, **kwargs):
                orgConnect(*args, **kwargs)
                sock = getattr(conn, "sock")
                if sock:
                    try:
                        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                    except Exception:  # nosec
                        pass

            conn.connect = ConnectDisableNagle

    ## Need to override the depcopy method. Since, the stub is not deep copyable
    #  due to the thread lock and connection pool, deep copy of a managed object
    #  fails. Further different instances of a managed object still share the
    #  same soap stub. Hence, returning self here is fine.
    def __deepcopy__(self, memo):
        return self


HEADER_SECTION_END = "\r\n\r\n"


## Parse an HTTP response into its headers and body
def ParseHttpResponse(httpResponse):
    headerEnd = httpResponse.find(HEADER_SECTION_END)
    if headerEnd == -1:
        return ("", "")
    headerEnd += len(HEADER_SECTION_END)
    headerText = httpResponse[:headerEnd]
    bodyText = httpResponse[headerEnd:]
    return (headerText, bodyText)


## SOAP-over-stdio stub adapter object
class SoapCmdStubAdapter(SoapStubAdapterBase):
    ## Constructor
    #
    # @param self self
    # @param cmd command to execute
    # @param ns API namespace
    def __init__(self, cmd, version="vim.version.version9"):
        SoapStubAdapterBase.__init__(self, version=version)
        self.cmd = cmd
        self.systemError = GetVmodlType("vmodl.fault.SystemError")

    ## Invoke a managed method
    #
    # @param self self
    # @param mo the 'this'
    # @param info method info
    # @param args arguments
    def InvokeMethod(self, mo, info, args):
        argv = self.cmd.split()
        req = self.SerializeRequest(mo, info, args)
        env = dict(os.environ)
        env["REQUEST_METHOD"] = "POST"
        env["CONTENT_LENGTH"] = str(len(req))
        env["HTTP_SOAPACTION"] = self.versionId[1:-1]
        p = subprocess.Popen(  # nosec
            argv,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )  # nosec
        (outText, errText) = p.communicate(req)
        if p.returncode < 0:
            # Process died with a signal
            errText = "Process terminated with signal %d\n%s" % (-p.returncode, errText)
            raise self.systemError(msg=errText, reason=errText)

        try:
            (responseHeaders, responseBody) = ParseHttpResponse(outText)
            obj = SoapResponseDeserializer(self).Deserialize(responseBody, info.result)
        except:
            errText = "Failure parsing SOAP response (%s)\n%s" % (outText, errText)
            raise self.systemError(msg=errText, reason=errText)

        if p.returncode == 0:
            return obj
        elif obj is None:
            raise self.systemError(msg=errText, reason=errText)
        else:
            raise obj  # pylint: disable-msg=E0702


class SessionOrientedStub(StubAdapterBase):
    """A session-oriented stub adapter that will relogin to the destination if a
    session-oriented exception is thrown.


    Here's an example.  First, we setup the communication substrate:

    >>> soapStub = SoapStubAdapter(host="192.168.1.2", ns="vim25/5.5")

    Create a SessionOrientedStub that uses the stub we just created for talking
    to the server:

    >>> from pyVim.connect import VimSessionOrientedStub
    >>> sessionStub = VimSessionOrientedStub(
    ...     soapStub,
    ...     VimSessionOrientedStub.makeUserLoginMethod("root", "vmware"))

    Perform some privileged operations without needing to explicitly login:

    >>> si = Vim.ServiceInstance("ServiceInstance", sessionStub)
    >>> si.content.sessionManager.sessionList
    >>> si.content.sessionManager.Logout()
    >>> si.content.sessionManager.sessionList
    """

    STATE_UNAUTHENTICATED = 0
    STATE_AUTHENTICATED = 1

    SESSION_EXCEPTIONS = tuple()

    def __init__(self, soapStub, loginMethod, retryDelay=0.1, retryCount=4):
        """Construct a SessionOrientedStub.

        The stub starts off in the "unauthenticated" state, so it will call the
        loginMethod on the first invocation of a method.  If a communication error
        is encountered, the stub will wait for retryDelay seconds and then try to
        call the method again.  If the server throws an exception that is in the
        SESSION_EXCEPTIONS tuple, it will be caught and the stub will transition
        back into the "unauthenticated" state so that another login will be
        performed.

        @param soapStub The communication substrate.
        @param loginMethod A function that takes a single parameter, soapStub, and
          performs the necessary operations to authenticate with the server.
        @param retryDelay The amount of time to sleep before retrying after a
          communication error.
        @param retryCount The number of times to retry connecting to the server.
        """
        assert callable(loginMethod)  # nosec
        assert retryCount >= 0  # nosec
        StubAdapterBase.__init__(self, version=soapStub.version)

        self.lock = threading.Lock()
        self.soapStub = soapStub
        self.state = self.STATE_UNAUTHENTICATED

        self.loginMethod = loginMethod
        self.retryDelay = retryDelay
        self.retryCount = retryCount

    def InvokeMethod(self, mo, info, args):
        # This retry logic is replicated in InvokeAccessor and the two copies need
        # to be in sync
        retriesLeft = self.retryCount
        while True:
            try:
                if self.state == self.STATE_UNAUTHENTICATED:
                    self._CallLoginMethod()
                # Invoke the method
                status, obj = self.soapStub.InvokeMethod(mo, info, args, self)
            except (
                socket.error,
                six.moves.http_client.HTTPException,
                ExpatError,
            ) as ex:
                if self.retryDelay and retriesLeft:
                    time.sleep(self.retryDelay)
                retriesLeft -= 1
                if retriesLeft <= 0:
                    raise ex
                continue

            if status == 200:
                # Normal return from the server, return the object to the caller.
                return obj

            # An exceptional return from the server
            if isinstance(obj, self.SESSION_EXCEPTIONS):
                # Our session might've timed out, change our state and retry.
                self._SetStateUnauthenticated()
            else:
                # It's an exception from the method that was called, send it up.
                raise obj

    ## Retrieve a managed property
    #
    # @param self self
    # @param mo managed object
    # @param info property info
    def InvokeAccessor(self, mo, info):
        # This retry logic is replicated in InvokeMethod and the two copies need
        # to be in sync
        retriesLeft = self.retryCount
        while True:
            try:
                if self.state == self.STATE_UNAUTHENTICATED:
                    self._CallLoginMethod()
                # Invoke the method
                obj = StubAdapterBase.InvokeAccessor(self, mo, info)
            except (
                socket.error,
                six.moves.http_client.HTTPException,
                ExpatError,
            ) as ex:
                if self.retryDelay and retriesLeft:
                    time.sleep(self.retryDelay)
                retriesLeft -= 1
                if retriesLeft <= 0:
                    raise ex
                continue
            except Exception as e:
                if isinstance(e, self.SESSION_EXCEPTIONS):
                    # Our session might've timed out, change our state and retry.
                    self._SetStateUnauthenticated()
                else:
                    raise e
            return obj

    ## Handle the login method call
    #
    #  This method calls the login method on the soap stub and changes the state
    #  to authenticated
    def _CallLoginMethod(self):
        try:
            self.lock.acquire()
            if self.state == self.STATE_UNAUTHENTICATED:
                self.loginMethod(self.soapStub)
                self.state = self.STATE_AUTHENTICATED
        finally:
            self.lock.release()

    ## Change the state to unauthenticated
    def _SetStateUnauthenticated(self):
        self.lock.acquire()
        if self.state == self.STATE_AUTHENTICATED:
            self.state = self.STATE_UNAUTHENTICATED
        self.lock.release()
