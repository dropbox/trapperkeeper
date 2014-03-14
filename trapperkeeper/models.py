from datetime import datetime
import os
import subprocess

from sqlalchemy import create_engine
from sqlalchemy import (
    Column, Integer, String, LargeBinary,
    ForeignKey, Enum, DateTime, BigInteger
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker

from constants import NAME_TO_PY_MAP, SNMP_TRAP_OID, ASN_TO_NAME_MAP


Session = sessionmaker()
Model = declarative_base()

def get_db_engine(url):
    return create_engine(url, pool_recycle=300)


class Notification(Model):

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)

    sent = Column(DateTime, default=datetime.now)
    expires = Column(DateTime, default=None, nullable=True)
    host = Column(String(length=255))
    trap_type = Column(Enum("trap", "trap2", "inform"))
    version = Column(Enum("v1", "v2c", "v3"))
    request_id = Column(BigInteger)
    oid = Column(String(length=1024))

    def pprint(self):
        print "Host:", self.host
        print "Trap Type:", self.trap_type
        print "Request ID:", self.request_id
        print "Version:", self.version
        print "Trap OID:", self.oid
        print "VarBinds:"
        for varbind in self.varbinds:
            varbind.pprint()

    @staticmethod
    def _from_pdu_v1(host, proto_module, version, pdu):
        trapoid = str(proto_module.apiTrapPDU.getEnterprise(pdu))

        generic = int(proto_module.apiTrapPDU.getGenericTrap(pdu))
        specific = int(proto_module.apiTrapPDU.getSpecificTrap(pdu))

        if generic == 6:  # Enterprise Specific Traps
            trapoid = "%s.0.%s" % (trapoid, specific)
        else:
            trapoid = "%s.%s" % (trapoid, generic + 1)

        trap_type = "trap"
        # v1 doesn't have request_id. Use timestamp in it's place.
        request_id = int(proto_module.apiTrapPDU.getTimeStamp(pdu))

        now = datetime.now()
        trap = Notification(host=host, sent=now, trap_type=trap_type, request_id=request_id, version=version, oid=trapoid)

        for oid, val in proto_module.apiTrapPDU.getVarBinds(pdu):
            oid = oid.prettyPrint()
            pval = val.prettyPrint()
            val_type = ASN_TO_NAME_MAP.get(val.__class__, "octet")
            trap.varbinds.append(VarBind(oid=oid, value_type=val_type, value=pval))

        return trap

    @staticmethod
    def _from_pdu_v2c(host, proto_module, version, pdu):
        varbinds = []
        trapoid = None
        trap_type = "trap2"
        request_id = proto_module.apiTrapPDU.getRequestID(pdu).prettyPrint()

        # Need to do initial loop to pull out trapoid
        for oid, val in proto_module.apiPDU.getVarBindList(pdu):
            oid = oid.prettyPrint()
            val = val.getComponentByName("value").getComponent().getComponent()
            pval = val.prettyPrint()

            if oid == SNMP_TRAP_OID:
                trapoid = pval
                continue

            varbinds.append((oid, ASN_TO_NAME_MAP.get(val.__class__, "octet"), pval))

        if not trapoid:
            return

        now = datetime.now()
        trap = Notification(host=host, sent=now, trap_type=trap_type, request_id=request_id, version=version, oid=trapoid)
        for oid, val_type, val in varbinds:
            trap.varbinds.append(VarBind(oid=oid, value_type=val_type, value=val))

        return trap

    @staticmethod
    def from_pdu(host, proto_module, version, pdu):
        if version == "v1":
            return Notification._from_pdu_v1(host, proto_module, version, pdu)
        elif version == "v2c":
            return Notification._from_pdu_v2c(host, proto_module, version, pdu)
        else:
            return None


class VarBind(Model):

    __tablename__ = "varbinds"

    id = Column(Integer, primary_key=True)

    notification_id = Column(Integer, ForeignKey("notifications.id"), index=True)
    notification = relationship(Notification, backref=backref("varbinds"))
    oid = Column(String(length=1024))
    value_type = Column(Enum(*NAME_TO_PY_MAP.keys()))
    value = Column(LargeBinary)

    def pprint(self):
        print "\t", self.oid, "(%s)" % self.value_type, "=", self.value

    def __repr__(self):
        return "Varbind(oid=%s, value_type=%s, value=%s)" % (
            repr(self.oid), repr(self.value_type), repr(self.value)
        )
