from datetime import datetime
from sqlalchemy import desc, func, or_

from trapdoor.utils import TrapdoorHandler
from trapperkeeper.models import Notification


class Index(TrapdoorHandler):
    def get(self):

        now = datetime.utcnow()
        offset = int(self.get_argument("offset", 0))
        limit = int(self.get_argument("limit", 50))
        hostname = self.get_argument("hostname", None)
        oid = self.get_argument("oid", None)

        active_query = (self.db
            .query(Notification)
            .filter(or_(
                Notification.expires >= now,
                Notification.expires == None
             ))
            .order_by(desc(Notification.sent))
        )

        if hostname is not None:
            active_query = active_query.filter(Notification.host == hostname)

        if oid is not None:
            active_query = active_query.filter(Notification.oid == oid)

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

            if hostname is not None:
                expired_query = expired_query.filter(Notification.host == hostname)

            if oid is not None:
                expired_query = expired_query.filter(Notification.oid == oid)

            traps += expired_query.offset(remaining_offset).limit(limit - num_active).all()

        return self.render(
            "index.html", traps=traps, now=now, num_active=num_active,
            hostname=hostname, oid=oid, offset=offset, limit=limit)

class Traps(TrapdoorHandler):
    def get(self):
        hostname = self.get_argument("hostname")
        oid = self.get_argument("oid")

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

