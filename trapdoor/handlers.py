from datetime import datetime
import json
from sqlalchemy import desc, func, or_

from trapdoor.utils import TrapdoorHandler
from trapperkeeper.models import Notification, VarBind

def filter_query(query, hostname, oid, severity):
    if hostname is not None:
        query = query.filter(Notification.host == hostname)

    if oid is not None:
        query = query.filter(Notification.oid == oid)

    if severity is not None:
        query = query.filter(Notification.severity == severity)

    return query


class Index(TrapdoorHandler):
    def get(self):

        now = datetime.utcnow()

        offset = int(self.get_argument("offset", 0))
        limit = int(self.get_argument("limit", 50))
        if limit > 100:
            limit = 100

        hostname = self.get_argument("hostname", None)
        oid = self.get_argument("oid", None)
        severity = self.get_argument("severity", None)

        active_query = (self.db
            .query(Notification)
            .filter(or_(
                Notification.expires >= now,
                Notification.expires == None
             ))
            .order_by(desc(Notification.sent))
        )
        active_query = filter_query(active_query, hostname, oid, severity)

        total_active = active_query.count()
        traps = active_query.offset(offset).limit(limit).all()
        num_active = len(traps)

        if num_active:
            remaining_offset = 0
        else:
            remaining_offset = offset - total_active
            if remaining_offset < 0:
                remaining_offset = 0

        if num_active < limit:
            expired_query = (self.db
                .query(Notification)
                .filter(Notification.expires < now)
                .order_by(desc(Notification.sent))
            )
            expired_query = filter_query(expired_query, hostname, oid, severity)
            traps += expired_query.offset(remaining_offset).limit(limit - num_active).all()

        return self.render(
            "index.html", traps=traps, now=now, num_active=num_active,
            hostname=hostname, oid=oid, severity=severity, offset=offset, limit=limit)

class Resolve(TrapdoorHandler):
    def post(self):
        hostname = self.get_argument("host")
        oid = self.get_argument("oid")

        now = datetime.utcnow()

        traps = (self.db.query(Notification)
            .filter(
                Notification.host == hostname,
                Notification.oid == oid,
                or_(
                    Notification.expires >= now,
                    Notification.expires == None
                )
            )
            .all()
        )

        for trap in traps:
            trap.expires = now
        self.db.commit()

        return self.redirect("/")

class ResolveAll(TrapdoorHandler):
    def post(self):

        now = datetime.utcnow()
        traps = (self.db.query(Notification)
            .filter(
                or_(
                    Notification.expires >= now,
                    Notification.expires == None
                )
            )
            .all()
        )

        for trap in traps:
            trap.expires = now
        self.db.commit()

        return self.redirect("/")

class NotFound(TrapdoorHandler):
    def get(self):
        return self.notfound()


class ApiVarBinds(TrapdoorHandler):
    def get(self, notification_id):
        varbinds = self.db.query(VarBind).filter(VarBind.notification_id == notification_id).all()
        varbinds = [varbind.to_dict(True) for varbind in varbinds]
        self.write(json.dumps(varbinds))


class ApiActiveTraps(TrapdoorHandler):
    def get(self):

        now = datetime.utcnow()
        hostname = self.get_argument("hostname", None)
        oid = self.get_argument("oid", None)
        severity = self.get_argument("severity", None)

        active_query = (self.db
            .query(
                Notification.host,
                Notification.oid,
                Notification.severity)
            .filter(or_(
                Notification.expires >= now,
                Notification.expires == None
             ))
            .group_by(Notification.host, Notification.oid)
            .order_by(desc(Notification.sent))
        )
        active_query = filter_query(active_query, hostname, oid, severity)

        traps = active_query.all()
        self.write(json.dumps(traps))
